"""
Command line interface.

Global options are defined here.
Command-specific options are defined by each command.

"""
import os
import argparse

from opbeatcli import __version__
from opbeatcli import settings
from opbeatcli.commands import COMMANDS


parser = argparse.ArgumentParser(
    description='Interact with Opbeat',
    version=__version__,
)


### Common options

parser.add_argument(
    '--verbose',
    help='Increase output verbosity',
    action='store_true'
)

common = parser.add_argument_group('common options')

common.add_argument(
    '-o', '--org-id',
    required=True,
    dest='organization_id',
    default=os.environ.get('OPBEAT_ORGANIZATION_ID'),
    help='Can be also set via the environment variable'
         ' OPBEAT_ORGANIZATION_ID.',
)
common.add_argument(
    '-a', '--app-id',
    help='Can be also set with environment variable'
         ' OPBEAT_APP_ID.',
    dest='app_id',
    required=True,
    default=os.environ.get('OPBEAT_APP_ID')
)
common.add_argument(
    '-t',
    '--secret-token',
    action='store',
    dest='secret_token',
    default=os.environ.get('OPBEAT_ACCESS_TOKEN'),
    help='Can be also set via the environment variable'
         ' OPBEAT_SECRET_TOKEN.',
)
common.add_argument(
    '-s',
    '--server',
    action='store',
    dest='server',
    default=os.environ.get('OPBEAT_SERVER', settings.SERVER),
    help='Use another remote server than the default one (%s).'
         ' Can be also set via the environment'
         ' variable OPBEAT_SERVER'
        % settings.SERVER,
)
common.add_argument(
    '--timeout',
    action='store',
    dest='timeout',
    type=float,
    default=settings.TIMEOUT,
    help='Use another remote server than the default one (%s).'
         ' Can be also set via the environment'
         ' variable OPBEAT_SERVER'
        % settings.SERVER,
)


### Add command sub-parsers.

subparsers = parser.add_subparsers()
for name, Command in COMMANDS.items():
    subparser = subparsers.add_parser(name=name)
    Command.add_command_args(subparser)
    subparser.set_defaults(command_class=Command)
