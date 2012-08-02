"""
opbeat.runner
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging
import os
import sys
import pwd

import argparse
from opbeat.command import load_all_commands
from opbeat.commands.login import login, LoginError
from opbeat.conf import defaults
from opbeat.credentials import load_credentials,get_default_filename
from opbeat.client import Client
from opbeat.version import VERSION
from opbeat.utils import query_yes_no

def set_shared_options(parser):
	parser.add_argument(
		"-s", "--server",action="store", dest="server",
		help="Override remote server. Can be set with environment variable OPBEAT_SERVER",
		default=os.environ.get('OPBEAT_SERVER', defaults.SERVER)
	)

	parser.add_argument("-t", "--access-token",action="store",
					dest="access_token",
					help="Set access token. Can be set with environment variable OPBEAT_ACCESS_TOKEN",
					default=os.environ.get('OPBEAT_ACCESS_TOKEN')
	)
	
	parser.add_argument("--verbose", help="Increase output verbosity",
					action="store_true")

	parser.add_argument(
		"-c", "--config-file",
		help="Specify config file. Can be set with environment variable OPBEAT_CONFIG_FILE. Defaults to '%s' " % get_default_filename(),
		action="store",default=os.environ.get('OPBEAT_CONFIG_FILE', get_default_filename())
		)

def build_client(project_id, server, logger, client_id, dry_run = False, access_token=None, config_file = None):
	if not access_token:
		logger.info("ERROR: No credentials detected!")
		query = "We can log you in now and obtain access credentials.\n"
		query += "The credentials would be saved to: %s\n" % (config_file or get_default_filename())
		query += "If you have an access token, you can use -t or OPBEAT_ACCESS_TOKEN env variable\n"
		query += "Would you like to log in now?"
		if query_yes_no(query):
			try:
				access_token =login(logger, server, client_id)
			except LoginError, ex:
				logger.error(ex)
				logger.info("Can not continue")
				return False
			except KeyboardInterrupt:
				return False
		else:
			return False

	client = Client(project_id=project_id, access_token=access_token, server = server, logger=logger, dry_run=dry_run)

	logger.info( "Client configuration:" )
	for k in ('server', 'project_id'):
		logger.info( '  %-15s: %s' % (k, getattr(client, k)) )
	print

	if not all([client.server, client.access_token]):
		logger.info( "Error: All values must be set!" )
		return False

	return client

def get_parser():
	parser = argparse.ArgumentParser(
		description="Interact with Opbeat (v%s)" % VERSION)

	set_shared_options(parser)
	# Returns a list of classes
	commands = load_all_commands()
	sub_parsers = parser.add_subparsers()
	for cmd in commands:
		# Each object will add itself to the mother-parser
		cmd(sub_parsers)

	return parser

def main():
	root = logging.getLogger('opbeat.errors')
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

			# Load credentials from config file
			if not args.access_token:
				credentials = load_credentials(args.config_file)
				if credentials:
					args.access_token = credentials['access_token']

			args.func(args, root)
		except Exception, ex:
			if args.verbose:
				root.exception("Error executing command")
			else:
				root.error(ex)

if __name__ == '__main__':
	main()
