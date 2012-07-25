"""
opbeat.credentials
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


from pkgutil import walk_packages
import opbeat.commands
import sys
import logging

from client import Client

def load_all_commands():
	return filter(lambda x: x is not None, [load_command(name) for name in command_names()])
		
def load_command(name):
    full_name = 'opbeat.commands.%s' % name
    if full_name in sys.modules:
        return None
    try:
        __import__(full_name)
        return sys.modules[full_name].command
    except ImportError, ex:
    	print ex

def command_names():
	names = set((pkg[1] for pkg in walk_packages(path=opbeat.commands.__path__)))
	return list(names)

import argparse

command_dict = {}

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

		self._build_client()

	def _build_client(self):
		## Load 
		pass

	def add_args(self):
		pass

	def setup_logging(self, args):
		self.logger = logging.getLogger('opbeat.command.%s' % self.name)

		if args.verbose:
			level = logging.DEBUG
		else:
			level = logging.INFO

		self.logger.setLevel(level)
		
		ch = logging.StreamHandler()
		# ch.setLevel(logging.DEBUG)

		self.logger.addHandler(ch)

	def run_first(self, args):
		self.setup_logging(args)
		self.run(args)

	def run(self, args):
		raise NotImplemented