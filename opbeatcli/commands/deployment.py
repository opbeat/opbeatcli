import os
import argparse
from collections import namedtuple, defaultdict

from opbeatcli import settings
from opbeatcli.deployment import get_deployment_data
from opbeatcli.exceptions import InvalidArgumentError
from .base import CommandBase


class KeyValue(namedtuple('BaseKeyValue', ['key', 'value'])):

    @classmethod
    def from_string(cls, string):
        try:
            key, value = string.split('=', 1)
            if not (key and value):
                raise ValueError()
        except ValueError:
            raise InvalidArgumentError(
                'not a key=value pair: %r' % string
            )
        return cls(key, value)


class RepoSpecValidator(object):

    def __init__(self, **schema):
        """
        Schema is a ``dict`` where keys are allowed keys, and their
        ``bool`` values indicate whether the field is required or not.

        """
        self.schema = schema
        self.allowed = set(self.schema.keys())
        self.required = set(
            field for field, required in self.schema.items() if required
        )

    def __call__(self, pairs):
        """
        Parse a repo spec key-value pairs into a dict.

        Simple validation of keys/values is performed according
        to ``self.schema``.

        """

        keys, values = zip(*pairs)
        keys_set = set(keys)

        unknown_keys = keys_set - self.allowed
        missing_keys = self.required - keys_set
        has_duplicate_keys = len(keys) > len(keys_set)

        if unknown_keys:
            raise InvalidArgumentError(
                'unknown keys: %s'
                % ', '.join(unknown_keys)
            )
        if missing_keys:
            raise InvalidArgumentError(
                'missing keys : %s'
                % ', '.join(unknown_keys)
            )
        if has_duplicate_keys:
            counter = defaultdict(int)
            for key in keys:
                counter[key] += 1
            duplicates = [key for key, count in counter.items() if count > 1]
            raise InvalidArgumentError(
                'duplicate keys: %s' % ', '.join(duplicates)
            )

        spec = dict(zip(keys, values))

        # Add default values for optional keys that are not specified.
        for field in self.allowed:
            if field not in spec:
                spec[field] = None

        return spec


repo_spec_validator = RepoSpecValidator(
    name=True,
    vcs=False,
    remote_url=False,
    branch=False,
    rev=False,
    version=False
)
local_repo_spec_validator = RepoSpecValidator(
    path=True,
    name=False,
    version=False
)


class DeploymentCommand(CommandBase):

    name = 'deployment'
    description = 'Send deployment info.'

    def run(self):

        local_repo_specs = self.args.local_repo_specs or []
        repo_specs = self.args.repo_specs or []

        if self.args.legacy_directory or self.args.legacy_module:
            if self.args.local_repo_specs:
                self.parser.error(
                    '--directory, -d and --module, -m'
                    ' cannot be used together with --repo.'
                )

            self.logger.warning(
                'Warning: --directory, -d and --module, -m are deprecated and'
                ' will be removed in a future version of opbeatcli.'
                '\nPlease use --repo instead. See ` opbeat deployment --help\''
                ' for more details.'
            )

            spec = [
                KeyValue('path', self.args.legacy_directory or os.getcwd())
            ]
            if self.args.legacy_module:
                spec.append(KeyValue('name', self.args.legacy_module))
            local_repo_specs.append(spec)

        if not local_repo_specs:
            local_repo_specs.append(
                [KeyValue('path', os.getcwd())]
            )

        try:
            data = get_deployment_data(
                local_hostname=self.args.hostname,
                local_repo_specs=map(
                    local_repo_spec_validator,
                    local_repo_specs
                ),
                repo_specs=map(
                    repo_spec_validator,
                    repo_specs or []
                ),
            )
        except InvalidArgumentError as e:
            self.parser.error(e.message)
        else:
            self.client.post(uri=settings.DEPLOYMENT_API_URI, data=data)

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
            help='Override hostname of current machine. '
                 'Can be set with environment variable OPBEAT_HOSTNAME',
        )
        subparser.add_argument(
            '--local-repo',
            action='append',
            dest='local_repo_specs',
            nargs=argparse.ZERO_OR_MORE,
            metavar='LOCAL_REPO_SPEC',
            type=KeyValue.from_string,
            help='',
        )
        subparser.add_argument(
            '--repo',
            nargs=argparse.ZERO_OR_MORE,
            dest='repo_specs',
            metavar='REPO_SPEC',
            action='append',
            type=KeyValue.from_string,
            help='',
        )
        subparser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help="Don't send anything. Use --verbose to print the request.",
        )

        # Hidden aliases for --repository to preserve
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
