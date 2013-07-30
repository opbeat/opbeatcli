"""
Command line interface.

Global options are defined here.
Command-specific options are defined by each command.

"""
import os
import argparse
from textwrap import dedent

from opbeatcli import __version__
from opbeatcli import settings
from opbeatcli.commands import COMMANDS


class OpbeatHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    A formatter that does not format our help strings.

    """

    def __init__(self, max_help_position=8, *args, **kwargs):
        # A smaller indent for args help.
        kwargs['max_help_position'] = max_help_position
        super(OpbeatHelpFormatter, self).__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        text = dedent(text).strip() + '\n\n'
        return text.splitlines()


parser = argparse.ArgumentParser(
    description='Interact with Opbeat',
    version=__version__,
    formatter_class=OpbeatHelpFormatter
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
    help='Can be also set via the environment variable OPBEAT_ORGANIZATION_ID.',
)
common.add_argument(
    '-a', '--app-id',
    help='Can be also set with environment variable OPBEAT_APP_ID.',
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
    help="""
        Can be also set via the environment variable OPBEAT_SECRET_TOKEN.
    """,
)
common.add_argument(
    '-s',
    '--server',
    action='store',
    dest='server',
    default=os.environ.get('OPBEAT_SERVER', settings.SERVER),
    help="""
        Use another remote server than the default one (%s).
        It can also be set via the environment variable OPBEAT_SERVER
    """ % settings.SERVER,
)
common.add_argument(
    '--timeout',
    action='store',
    dest='timeout',
    type=float,
    default=settings.TIMEOUT,
    help='Time for the connection phase of HTTP requests.',
)


### Add command sub-parsers.

subparsers = parser.add_subparsers()
for name, Command in COMMANDS.items():
    subparser = subparsers.add_parser(
        name=name,
        formatter_class=OpbeatHelpFormatter
    )
    Command.add_command_args(subparser)
    subparser.set_defaults(command_class=Command)
