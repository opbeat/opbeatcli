import os
#noinspection PyCompatibility
import argparse
from collections import namedtuple, defaultdict

from opbeatcli import settings
from opbeatcli.log import logger
from opbeatcli.exceptions import InvalidArgumentError
from opbeatcli.deployment import get_deployment_data
from opbeatcli.deployment.vcs import VCS_NAME_MAP
from opbeatcli.deployment.packages import (DEPENDENCY_COLLECTORS,
                                           DEPENDENCIES_BY_TYPE)
from .base import CommandBase


class KeyValue(namedtuple('BaseKeyValue', ['key', 'value'])):
    """A key-value tuple."""

    separator = ':'

    @classmethod
    def from_string(cls, string):
        try:
            key, value = string.split(cls.separator, 1)
            if not (key and value):
                raise ValueError()
        except ValueError:
            raise InvalidArgumentError(
                'not a key%svalue pair: %r' % (cls.separator, string)
            )
        return cls(key, value)


class KeyOptionalValue(KeyValue):

    @classmethod
    def from_string(cls, string):
        if cls.separator in string:
            return super(KeyOptionalValue, cls).from_string(string)
        return cls(string, None)


class PackageSpecValidator(object):

    def __init__(self, _name, **schema):
        """
        Schema is a ``dict`` where keys are allowed keys, and their
        ``bool`` values indicate whether the field is required or not.

        """
        self.name = _name
        self.schema = schema
        self.allowed = set(self.schema.keys())
        self.required = set(
            field for field, required in self.schema.items() if required
        )

    def validation_error(self, error_name, attributes):
        raise InvalidArgumentError(
            '{name}: {error_name} attribute{plural}: {attributes}'.format(
            name=self.name,
            error_name=error_name,
            plural='s' if len(attributes) > 1 else '',
            attributes=', '.join(sorted(attributes))
        ))

    def __call__(self, pairs):
        """
        Parse a package spec key-value pairs into a dict.

        Simple validation of keys/values is performed according
        to ``self.schema``.

        """

        keys, values = zip(*pairs)
        keys_set = set(keys)

        unknown_keys = keys_set - self.allowed
        missing_keys = self.required - keys_set
        has_duplicate_keys = len(keys) > len(keys_set)

        if unknown_keys:
            self.validation_error('unknown', unknown_keys)

        if missing_keys:
            self.validation_error('missing', missing_keys)

        if has_duplicate_keys:
            counter = defaultdict(int)
            for key in keys:
                counter[key] += 1
            duplicates = [key for key, count in counter.items() if count > 1]
            self.validation_error('duplicate', duplicates)

        spec = dict(zip(keys, values))

        # Add default values for optional keys that are not specified.
        for field in self.allowed:
            if field not in spec:
                spec[field] = None

        return spec


PACKAGE_SCHEMA = {'vcs': False, 'remote_url': False,
                  'branch': False, 'rev': False, 'version': False}


args_to_component_spec = PackageSpecValidator(
    '--component',
    path=True,
    name=False,
    **PACKAGE_SCHEMA
)
args_to_dependency_spec = PackageSpecValidator(
    '--dependency',
    name=True,
    type=True,
    **PACKAGE_SCHEMA
)


class DeploymentCommand(CommandBase):

    name = 'deployment'
    description = 'Send deployment info.'

    def run(self):

        if self.args.collect_dependency_types is None:
            collect_dep_types_specified = False
            collect_dep_types = []
        else:
            if not self.args.collect_dependency_types:
                collect_dep_types_specified = False
                collect_dep_types = DEPENDENCY_COLLECTORS.keys()
            else:
                collect_dep_types_specified = True
                collect_dep_types = self.args.collect_dependency_types

        component_specs, dependency_specs = self.get_package_specs()

        try:
            data = get_deployment_data(
                local_hostname=self.args.hostname,
                component_specs=component_specs,
                dependency_specs=dependency_specs,
                collect_dep_types=collect_dep_types,
                collect_dep_types_specified=collect_dep_types_specified,
            )
        except InvalidArgumentError as e:
            self.parser.error(e.message)
        else:
            self.client.post(uri=settings.DEPLOYMENT_API_URI, data=data)

    def get_package_specs(self):
        """
        Convert package args specified in the arguments into "spec" dicts
        using their validators.

        """
        component_specs = self.args.component_specs or []
        dependency_specs = self.args.dependency_specs or []

        if self.args.legacy_directory or self.args.legacy_module:
            if component_specs:
                self.parser.error(
                    '--directory, -d and --module, -m'
                    ' cannot be used together with --component.'
                )

            logger.warning(
                'Warning: --directory, -d and --module, -m are deprecated and'
                ' will be removed in a future version of opbeatcli.'
                '\nPlease use --component instead. '
                ' See ` opbeat deployment --help\''
                ' for more details.'
            )

            spec = [
                KeyValue('path', self.args.legacy_directory or os.getcwd())
            ]
            if self.args.legacy_module:
                spec.append(KeyValue('name', self.args.legacy_module))
            component_specs.append(spec)

        return [args_to_component_spec(spec) for spec in component_specs ],\
               [args_to_dependency_spec(spec) for spec in dependency_specs],


    @classmethod
    def add_command_args(cls, subparser):
        """
        :type subparser: argparse.ArgumentParser

        """
        subparser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help="Don't send anything. Use --verbose to print the request.",
        )
        subparser.add_argument(
            '--hostname',
            action='store',
            dest='hostname',
            default=os.environ.get('OPBEAT_HOSTNAME', settings.HOSTNAME),
            help="""
Override hostname of current machine. Can be set with environment variable
OPBEAT_HOSTNAME
            """,
        )

        subparser.add_argument(
            '--component',
            nargs=argparse.ONE_OR_MORE,
            dest='component_specs',
            metavar='attribute:value',
            action='append',
            type=KeyValue.from_string,
            help=r"""
                A description of a component of the app being deployed.
                Multiple components can be specified by using this option
                multiple times.

                Attributes:

                    path:<local-path>          (required)
                    name:<name>                (required)
                    version:<version-string>   (optional if VCS info specified)

                VCS attributes: if the provided path is a VCS checkout,
                these attributes will be filled automatically:

                    vcs:<{vcs_types}>
                    rev:<vcs-revision>
                    branch:<vcs-branch>
                    remote_url:<vcs-remote-url>

                A component has to have a name, and at least a version or rev.

                Examples:

                    --component path:.

                    --component \
                        path:frontends/web \
                        name:web-frontend \
                        version:0.2.1

                    --component \
                        path:tools/scheduler \
                        name:scheduler \
                        version:1.0.0-beta2
                        vcs:git \
                        rev:383dba \
                        branch:dev \
                        remote_url:git@github.com:opbeat/scheduler.git

            """
            .format(vcs_types='|'.join(sorted(VCS_NAME_MAP.values()))),
        )

        subparser.add_argument(
            '--dependency',
            nargs=argparse.ONE_OR_MORE,
            dest='dependency_specs',
            metavar='attribute:value',
            action='append',
            type=KeyValue.from_string,
            help=r"""
                A description of an installed third-party package that the app
                being deployed depends on. Multiple dependencies can be
                specified by using this option multiple times.

                Attributes are the same as with --component. There is no path,
                however. In addition to the common attributes, the type
                of the dependency has to be specified as well:

                    type:<{dependency_types}>

                A dependency has to have a name, and at least a version or rev.

                Examples:

                    --dependency type:other name:nginx version:1.5.3
                    --dependency type:python name:django version:1.5.0
                    --dependency type:ruby name:app2 vcs:git \
                                    rev:383dba branch:prod \
                                    remote_url:git@github.com:opbeat/app2.git

            """
            .format(
                vcs_types='|'.join(sorted(VCS_NAME_MAP.values())),
                dependency_types='|'.join(sorted(DEPENDENCIES_BY_TYPE.keys()))
            ),
        )

        subparser.add_argument(
            '--collect-dependencies',
            nargs=argparse.ZERO_OR_MORE,
            metavar='TYPE[:COMMAND]',
            dest='collect_dependency_types',
            type=KeyOptionalValue.from_string,
            help=r"""
            Enable automatic collection of installed dependencies.
            With no arguments, all the predefined dependency types will be
            attempted to collect. You can also choose to collect only some
            types of dependencies. The available types are:

                {types}

            Examples:

                --collect-dependencies
                --collect-dependencies python ruby

            For each type, there is one or more default shell commands which
            are run to collect the dependencies:

{default_commands}

            You can also supply one or more custom commands for each type as
            long as the output uses the same format as the default commands do:

            Collect only node.js dependencies using a custom command in
            addition to the default ones:

                --collect-dependencies \
                    nodejs \
                    nodejs:'cd /webapp2 && npm --local --json list' \

            Use only a custom collection command:

                --collect-dependencies \
                    python:'/my-virtualenv/bin/pip freeze'

            Default commands for some types, custom commands for others:

                --collect-dependencies \
                    python \
                    deb \
                    nodejs:'cd /www/webapp && npm --local --json list' \
                    ruby:'bin/script

            """
            .format(
                types=' '.join(sorted(DEPENDENCY_COLLECTORS.keys())),
                default_commands=''.join(sorted(
                    "{type: >23}: {commands}\n"
                    .format(
                        type=dep_type,
                        commands=('\n%s' % (' ' * 25)).join(
                            collector.default_commands
                        )
                    ).replace('%', '%%')  #
                    for dep_type, collector in DEPENDENCY_COLLECTORS.items()
                ))
            )
        )

        # Hidden aliases for --component to preserve
        # backward-compatibility with opbeatcli==1.1.5.
        subparser.add_argument(
            '-d', '--directory',
            dest='legacy_directory',
            help=argparse.SUPPRESS,
        )
        subparser.add_argument(
            '-m', '--module-name',
            dest='legacy_module',
            help=argparse.SUPPRESS,
        )
