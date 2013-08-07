"""
Command line interface.

Global options are defined here.
Command-specific options are defined by each command.

"""
import os
#noinspection PyCompatibility
import argparse
from textwrap import dedent

from opbeatcli import __version__
from opbeatcli import settings
from opbeatcli.commands import COMMANDS


class OpbeatHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """A nicer help formatter.

    Help for arguments can be indented and contain new lines.
    It will be de-dented and arguments in the help
    will be separated by a blank line for better readability.


    """
    def __init__(self, max_help_position=8, *args, **kwargs):
        # A smaller indent for args help.
        kwargs['max_help_position'] = max_help_position
        super(OpbeatHelpFormatter, self).__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        text = dedent(text).strip() + '\n\n'
        return text.splitlines()

    def format_help(self):
        text = super(OpbeatHelpFormatter, self).format_help()
        if text:
            text += '\n'
        return text

parser = argparse.ArgumentParser(
    description='Interact with Opbeat',
    formatter_class=OpbeatHelpFormatter
)


### Common options
parser.add_argument(
    '--version',
    action='version',
    version=__version__
)
common = parser.add_argument_group('common options')

common.add_argument(
    '--verbose',
    help='Increase output verbosity.',
    action='store_true'
)

common.add_argument(
    '--dry-run',
    action='store_true',
    dest='dry_run',
    help="""
    Don't send anything to the Opbeat API. Use --verbose to print the request.

    """,
)

common.add_argument(
    '-o', '--org-id',
    required=True,
    dest='organization_id',
    default=os.environ.get('OPBEAT_ORGANIZATION_ID'),
    help="""
    Can be also set via the environment variable OPBEAT_ORGANIZATION_ID.

    """,
)
common.add_argument(
    '-a', '--app-id',
    dest='app_id',
    required=True,
    default=os.environ.get('OPBEAT_APP_ID'),
    help="""
    Can be also set with environment variable OPBEAT_APP_ID.

    """,
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
        description=dedent(Command.DESCRIPTION),
        epilog=dedent(Command.EPILOG),
        formatter_class=OpbeatHelpFormatter,
    )
    Command.add_command_args(subparser)
    subparser.set_defaults(command_class=Command)
