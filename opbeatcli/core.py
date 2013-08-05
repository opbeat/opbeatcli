"""
Invoke as `opbeat` or `python -m opbeatcli`.

"""
import sys
import logging

from opbeatcli.log import logger
from opbeatcli.cli import parser
from opbeatcli.exceptions import OpbeatError, ClientConnectionError


EXIT_SUCCESS, EXIT_ERROR = 0, 1
EXIT_CLIENT_ERROR, EXIT_SERVER_ERROR = 4, 5


def get_command(args=sys.argv[1:]):
    args = parser.parse_args(args)
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    Command = args.command_class
    return Command(parser=parser, args=args)


def main(args=sys.argv[1:]):
    """Run command and return exit status code."""

    if len(sys.argv) < 2:
        parser.print_help()
        return EXIT_SUCCESS

    command = get_command(args)

    try:
        command.run()
    except ClientConnectionError as e:
        # The error has already been logged by the client.
        response_status = e.args[0]
        if response_status < 400:
            return EXIT_CLIENT_ERROR
        else:
            return EXIT_SERVER_ERROR
    except OpbeatError as e:
        logger.error(e.message)
        return EXIT_ERROR
    except Exception:
        logger.exception('Error executing command')
        return EXIT_ERROR
    else:
        return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
