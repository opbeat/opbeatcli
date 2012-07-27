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
from opbeat.conf import defaults
from opbeat.credentials import load_tokens
from opbeat.client import Client
from opbeat.version import VERSION

def set_shared_options(parser):
	parser.add_argument("-s", "--server",action="store",
					dest="server", help="override server. Can be set with environment variable OPBEAT_SERVER"),

	parser.add_argument("-t", "--access-token",action="store",
					dest="access_token", help="set access token. Can be set with environment variable OPBEAT_ACCESS_TOKEN"),
	
	parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")

def get_credentials(filename = None):
	try:
		return load_tokens(filename)
	except:
		return None

def build_client(project_id = None, access_token=None, server=None):
	creds = get_credentials()

	if not project_id:
		if os.environ.get('OPBEAT_PROJECT_ID'):
			project_id = os.environ.get('OPBEAT_PROJECT_ID')
	
	if not access_token:
		if os.environ.get('OPBEAT_ACCESS_TOKEN'):
			access_token = os.environ.get('OPBEAT_ACCESS_TOKEN')
		elif creds and 'access_token' in creds:
			access_token = creds['access_token']

	if not access_token:
		print "Error: No configuration detected!"
		print " - Use the 'login' command to log into the Opbeat platform and store access credentials locally or "
		print " - Set the OPBEAT_ACCESS_TOKEN environment variables or "
		print " - Use the -t / --access-token parameter to set an access token"
		print 
		return False

	if not server:
		if os.environ.get('OPBEAT_SERVER'):
			server = os.environ.get('OPBEAT_SERVER')
		else:
			server = defaults.SERVER
 # include_paths=['opbeat_python'],
	client = Client(project_id=project_id, access_token=access_token, server = server)

	print "Client configuration:"
	for k in ('server', 'project_id'):
		print '  %-15s: %s' % (k, getattr(client, k))
	print

	if not all([client.server, client.access_token]):
		print "Error: All values must be set!"
		print 
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
	root.setLevel(logging.DEBUG)
	root.addHandler(logging.StreamHandler())
	
	
	parser = get_parser()
	if len(sys.argv) < 2:
		parser.print_help()
	else:
		args = parser.parse_args()
		args.func(args)


	# client = build_client(options.project_id, options.api_key, options.server)

	# if not client:
	# 	parser.print_help()
	# 	return


	# if len(args) < 1 or args[0] not in pos_args:
	# 	parser.print_help()
	# else:
	# 	pos_args[args[0]](client, args[1:])

# if __name__ == "__main__" and __package__ is None:
#     __package__ = "opbeat_python"

if __name__ == '__main__':
	main()
