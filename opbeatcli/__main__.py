"""
Invoke as `opbeat` or `python -m opbeatcli`.

"""
import sys
import logging

from opbeatcli.log import root_logger
from opbeatcli.cli import parser
from opbeatcli.exceptions import OpbeatClientConnectionError


SUCCESS, ERROR = 0, 1
REQUEST_ERROR, SERVER_ERROR = 4, 5


def main():
    """Run command and return exit status code."""

    if len(sys.argv) < 2:
        parser.print_help()
        return SUCCESS

    args = parser.parse_args()

    root_logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    Command = args.command_class
    command = Command(args=args, logger=root_logger)

    try:
        command.run()
    except OpbeatClientConnectionError as e:
        # The error has already been logged by the client.
        response_status = e.args[0]
        if response_status < 400:
            return REQUEST_ERROR
        else:
            return SERVER_ERROR

    except Exception:
        root_logger.exception('Error executing command')
        return ERROR
    else:
        return SUCCESS


if __name__ == '__main__':
    sys.exit(main())
