import os
import argparse

from opbeatcli import settings
from opbeatcli.deployment import get_deployment_data, REPO_SPEC_RE
from opbeatcli.exceptions import InvalidArgumentError
from .base import CommandBase


class RepoSpecType(object):

    def __call__(self, string):
        if not REPO_SPEC_RE.match(string):
            raise argparse.ArgumentTypeError(
                'Invalid repo spec: %r' % string
            )
        return string


class DeploymentCommand(CommandBase):

    name = 'deployment'
    description = 'Send deployment info.'

    def run(self):

        if self.args.legacy_directory or self.args.legacy_module:
            if self.args.repo_specs:
                msg = (
                    'Error: --directory, -d and --module, -m'
                    ' cannot be used together with --repo.'
                )
                self.logger.error(msg)
                raise InvalidArgumentError(msg)

            self.logger.warning(
                'Warning: --directory, -d and --module, -m are deprecated and'
                ' will be removed in a future version of opbeatcli.'
                '\nPlease use --repo instead. See ` opbeat deployment --help\''
                ' for more details.'
            )

            spec = self.args.legacy_directory or os.getcwd()
            if self.args.legacy_module:
                spec = '{path}:{name}'.format(
                    path=spec,
                    name=self.args.legacy_module
                )
            self.args.repo_specs = [spec]

        if not self.args.repo_specs:
            self.args.repo_specs = [os.getcwd()]

        data = get_deployment_data(
            local_hostname=self.args.hostname,
            repo_specs=self.args.repo_specs,
        )
        self.client.post(uri=settings.DEPLOYMENT_API_URI, data=data)

    @classmethod
    def add_command_args(cls, subparser):

        subparser.add_argument(
            '--hostname',
            action='store',
            dest='hostname',
            default=os.environ.get('OPBEAT_HOSTNAME', settings.HOSTNAME),
            help='Override hostname of current machine. '
                 'Can be set with environment variable OPBEAT_HOSTNAME',
        )
        subparser.add_argument(
            '--repo',
            action='append',
            dest='repo_specs',
            metavar='REPO_SPEC',
            type=RepoSpecType(),
            help='"path[:name][@version]", examples:'
                 ' --repo=.'
                 ' --repo=/webapp'
                 ' --repo=/webapp:my-webapp'
                 ' --repo=/webapp@v1.0'
                 ' --repo=/webapp:my-webapp@v1.0',
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
            action='append',
            help=argparse.SUPPRESS,
            type=RepoSpecType(),
        )
        subparser.add_argument(
            '-m', '--module-name',
            dest='legacy_module',
            help=argparse.SUPPRESS,
        )
