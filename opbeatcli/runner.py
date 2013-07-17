"""
opbeatcli.runner
~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.

"""
import os
import sys
import logging
import argparse

from opbeatcli.command import load_all_commands
from opbeatcli.conf import defaults
from opbeatcli.client import Client
from opbeatcli.version import VERSION


def set_shared_options(parser):

    parser.add_argument(
        '-s',
        '--server',
        action='store',
        dest='server',
        help='Override remote server. Can be set with environment'
             ' variable OPBEAT_SERVER',
        default=os.environ.get('OPBEAT_SERVER', defaults.SERVER)
    )

    parser.add_argument(
        '-o', '--org-id',
        help='Use this organization id. Can be set with environment'
             ' variable OPBEAT_ORGANIZATION_ID',
        dest='organization_id',
        required=True,
        default=os.environ.get('OPBEAT_ORGANIZATION_ID')
    )

    parser.add_argument(
        '-a', '--app-id',
        help='Use this app id. Can be set with environment'
             ' variable OPBEAT_APP_ID',
        dest='app_id',
        required=True,
        default=os.environ.get('OPBEAT_APP_ID')
    )

    parser.add_argument(
        '-t',
        '--secret-token',
        action='store',
        dest='secret_token',
        help='Set secret token. Can be set with environment'
             ' variable OPBEAT_SECRET_TOKEN',
        default=os.environ.get('OPBEAT_ACCESS_TOKEN')
    )

    parser.add_argument(
        '--verbose',
        help='Increase output verbosity',
        action='store_true'
    )


def build_client(organization_id, app_id, secret_token,
                 server, logger, dry_run=False):

    if not secret_token:
        logger.error('ERROR: No secret token supplied!')
        return False

    client = Client(
        organization_id=organization_id,
        app_id=app_id,
        secret_token=secret_token,
        server=server,
        logger=logger,
        dry_run=dry_run
    )

    logger.info('Client configuration:')

    for k in ('server', 'organization_id', 'app_id'):
        logger.info('  %-15s: %s' % (k, getattr(client, k)))
    print

    if not all([client.server, client.organization_id,
                client.app_id, client.secret_token]):

        logger.info('Error: All values must be set!')

        return False

    return client


def get_parser():
    parser = argparse.ArgumentParser(
        description='Interact with Opbeat (v%s)' % VERSION)

    set_shared_options(parser)
    # Returns a list of classes
    commands = load_all_commands()
    sub_parsers = parser.add_subparsers()
    for cmd in commands:
        # Each object will add itself to the mother-parser
        cmd(sub_parsers)

    return parser


def main():
    root = logging.getLogger('opbeatcli.errors')
    root.addHandler(logging.StreamHandler())

    parser = get_parser()
    if len(sys.argv) < 2:
        parser.print_help()
    else:
        try:
            args = parser.parse_args()
            if args.verbose:
                root.setLevel(logging.DEBUG)
            else:
                root.setLevel(logging.INFO)

            args.func(args, root)
        except Exception:
            root.exception('Error executing command')


if __name__ == '__main__':
    main()
