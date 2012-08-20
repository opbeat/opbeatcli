"""
opbeat.credentials
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


from pkgutil import walk_packages
import opbeat.commands
from credentials import load_credentials
import sys
import logging
import argparse

from client import Client

def load_all_commands():
	return filter(lambda x: x is not None, [load_command(name) for name in command_names()])
		
def load_command(name):
	full_name = 'opbeat.commands.%s' % name

	try:
		if full_name not in sys.modules:
			__import__(full_name)
	except ImportError, ex:
		print ex
	else:
		return sys.modules[full_name].command

def command_names():
	names = set((pkg[1] for pkg in walk_packages(path=opbeat.commands.__path__)))
	return list(names)


# class SupportsDryRunMixin(object):
# 	def add_args(self):
# 		super(SupportsDryRunMixin, self).add_args()
# 		print "HELLO"
# 		self.parser.add_argument('-dr','--dry-run', help="Don't send anything. Use '--verbode' to print the request instead.", action="store_true", dest="dry_run")

class CommandBase(object):
	name = None
	usage = None
	hidden = False
	description = None

	login_required = True

	def __init__(self, subparsers):
		assert self.name

		self.parser = subparsers.add_parser(
			description=self.description,
			usage = self.usage,
			name=self.name
			)
		
		self.parser.set_defaults(func=self.run_first)

		self.add_args()


	def add_args(self):
		pass

	def run_first(self, args, logger):
		self.credentials = load_credentials(args.config_file)

		self.logger = logger
		self.run(args)

	def run(self, args):
		raise NotImplemented