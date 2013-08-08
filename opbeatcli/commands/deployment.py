import os
#noinspection PyCompatibility
import argparse
from collections import namedtuple, defaultdict
from operator import attrgetter
from itertools import chain, groupby

from opbeatcli import settings
from opbeatcli.log import logger
from opbeatcli.deployment.packages.component import Component
from opbeatcli.deployment.packages.base import BaseDependency
from opbeatcli.deployment import serialize
from opbeatcli.deployment.vcs import VCS_NAME_MAP
from opbeatcli.deployment.packages import (DEPENDENCY_COLLECTORS,
                                           DEPENDENCIES_BY_TYPE)
from opbeatcli.exceptions import (InvalidArgumentError,
                                  ExternalCommandNotFoundError)
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

    def __init__(self, _name='', **schema):
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
            '{name}: {error_name} attribute{plural}: {attributes}'
            .format(
                name=self.name,
                error_name=error_name,
                plural='s' if len(attributes) > 1 else '',
                attributes=', '.join(sorted(attributes))
            )
        )

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


PACKAGE_SCHEMA = {
    'vcs': False,
    'remote_url': False,
    'branch': False,
    'rev': False,
    'version': False
}


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


def collect_dependencies(type_command_args, ignore_no_command):

    get_type = attrgetter('key')
    get_command = attrgetter('value')

    groups = groupby(sorted(type_command_args, key=get_type), key=get_type)

    for dep_type, type_command_args in groups:

        try:
            collector_class = DEPENDENCY_COLLECTORS[dep_type]
        except KeyError:
            raise InvalidArgumentError(
                'Unknown dependency type to collect: %r' % dep_type
            )

        custom_commands = list(map(get_command, type_command_args))

        if len(custom_commands) != len(set(custom_commands)):
            raise InvalidArgumentError(
                'Duplicate dependency type: %s' % dep_type
            )

        commands = []
        for custom_command in custom_commands:
            if custom_command is None:
                commands.extend(collector_class.default_commands)
            else:
                commands.append(custom_command)

        collector = collector_class(custom_commands=commands)

        try:
            for dep in collector.collect():
                yield dep
        except ExternalCommandNotFoundError:
            if not ignore_no_command:
                # We can ignore this error unless the user explicitely asked
                # for this type (and also possibly supplied a custom command).
                raise


class DeploymentCommand(CommandBase):

    def run(self):
        self.logger.info('Registering deployment @ %s', self.args.hostname)
        try:
            data = self.get_data()
        except InvalidArgumentError as e:
            self.parser.error(e.message)
        else:
            self.logger.info('Sending data')
            self.client.post(uri=settings.DEPLOYMENT_API_URI, data=data)
            self.logger.info('Done')

    def get_data(self):
        packages = list(self.get_all_packages())

        component_count = sum(package.package_type == Component.package_type
                              for package in packages)
        self.logger.info('The app (%s) has %d components and %d dependencies',
                         self.args.app_id,
                         component_count,
                         len(packages) - component_count)

        return serialize.deployment(
            local_hostname=self.args.hostname,
            packages=packages,
        )

    def get_all_packages(self):
        return chain(
            self.get_packages_from_args(),
            self.collect_dependencies()
        )

    def collect_dependencies(self):
        if self.args.collect_deps is None:
            return []
        type_command_args = self.args.collect_deps or [
            KeyOptionalValue.from_string(type_)
            for type_ in DEPENDENCY_COLLECTORS.keys()
        ]

        self.logger.debug(
            'Starting dependency collection for %s',
            ', '.join(sorted(dict(type_command_args).keys()))
        )

        return collect_dependencies(
            type_command_args,
            ignore_no_command=not self.args.collect_deps,
        )

    def get_packages_from_args(self):
        """
        Convert package args specified in the arguments into "spec" dicts
        using their validators.

        """
        components = self.args.components or []
        dependencies = self.args.dependencies or []

        if self.args.legacy_directory or self.args.legacy_module:
            if components:
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

            attributes = [
                KeyValue('path', self.args.legacy_directory or os.getcwd())
            ]
            if self.args.legacy_module:
                attributes.append(KeyValue('name', self.args.legacy_module))
            components.append(attributes)

        components = [
            Component.from_spec(args_to_component_spec(attributes))
            for attributes in components
        ]

        dependencies = [
            BaseDependency.from_spec(args_to_dependency_spec(attributes))
            for attributes in dependencies
        ]

        self.logger.debug('Components from arguments: %d', len(components))
        for package in components:
            self.logger.debug('  %r', package)

        self.logger.debug('Dependencies from arguments: %d', len(dependencies))
        for package in dependencies:
            self.logger.debug('  %r', package)

        return components + dependencies

    DESCRIPTION = """
Introduction:
    This command registers a deployment of an application to a machine with
    the Opbeat API. Deployment tracking enables advanced features of the
    Opbeat platform, such as version history and the ability to relate errors
    with particular deployments, etc.

    It is meant to be run on the machine where the application is being
    deployed to. The data sent contains a list of installed packages
    (application components and dependencies) that all together make up the
    application and its runtime environment at the time of deployment.

    Component:
        A component is a named and versioned software package that is
        part of your application and is directly maintained by the
        organization. Many apps only consist of one main component, but others
        can have many individual components that together make up the
        application. Components need to specified manually on the command line.

    Dependency:
        A dependency is a named and versioned third-party software package the
        application in any way depends on or is part of its runtime
        environment. It can be a code library, a tool, server software, etc.
        Dependencies can be specified manually and/or automatically collected
        using this tool.

    Generally, the more information about installed packages is provided, the
    more useful deployment tracking becomes.


"""

    @classmethod
    def add_command_args(cls, subparser):
        """
        :type subparser: argparse.ArgumentParser

        """
        subparser.add_argument(
            '--hostname',
            action='store',
            dest='hostname',
            default=os.environ.get('OPBEAT_HOSTNAME', settings.HOSTNAME),
            help="""
            Override hostname of current machine. Can be set with environment
            variable OPBEAT_HOSTNAME.
            """,
        )

        subparser.add_argument(
            '--component',
            nargs=argparse.ONE_OR_MORE,
            dest='components',
            metavar='attribute:value',
            action='append',
            type=KeyValue.from_string,
            help=r"""
                A description of a component of the app being deployed.
                Multiple components can be specified by using this option
                multiple times.

                Attributes:

                    path:<local-path>          (required)
                    name:<name>                (optional)
                    version:<version-string>   (optional if VCS info specified)

                VCS attributes: if the provided path is a VCS checkout,
                these attributes will be filled automatically:

                    vcs:<{vcs_types}>
                    rev:<vcs-revision>
                    branch:<vcs-branch>
                    remote_url:<vcs-remote-url>

                A component has to have a path, and at least a version or rev.

                Examples:

                    --component path:.

                    --component \
                        path:frontends/web \
                        name:web-frontend \
                        version:0.2.1

                    --component \
                        path:tools/scheduler \
                        name:scheduler \
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
            dest='dependencies',
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
                dependency_types='|'.join(sorted(DEPENDENCIES_BY_TYPE.keys()))
            ),
        )

        subparser.add_argument(
            '--collect-dependencies',
            nargs=argparse.ZERO_OR_MORE,
            metavar='type[:command]',
            dest='collect_deps',
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
                        commands=('\n' + ' '*25).join(
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

    EPILOG = r"""
Examples:

    Single-component app in the current directory that is a VCS checkout,
    and default dependencies collection:

        $ opbeat deployment --collect-dependencies --component path:.

    Multiple components as VCS checkouts:

        $ opbeat deployment \
            --collect-dependencies \
            --component path:/project/frontend \
            --component path:/project/worker

    Components not present as VCS checkouts:

        $ opbeat deployment \
            --collect-dependencies \
            --component \
                path:/project/frontend \
                version:1.3.2 \
            --component \
                path:/project/backend \
                name:backend-server \
                version:1.6.0 \
                vcs:git \
                rev:383dba \
                branch:master \
                remote_url:git@github.com:example/backend-server.git

    Complex example:

        $ opbeat deployment \
            --component \
                name:pay-webapp \
                path:payments/frontend  \
            --component \
                name:pay-server \
                path:payments/server \
            --component \
                name:pay-worker \
                path:payments/worker \
                version:$(payments/worker/bin/worker --version) \
            --dependency \
                type:other \
                name:nginx \
                version:$(nginx -v 2>&1 | cut -d / -f 2) \
            --collect-dependencies \
                deb ruby python \
                python:'payments/server/virtualenv/bin/pip freeze' \
                nodejs:'cd payments/frontend && npm --local --json list'


"""
