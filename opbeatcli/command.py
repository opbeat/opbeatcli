"""
opbeatcli.credentials
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import sys
from pkgutil import walk_packages

import opbeatcli.commands


def load_all_commands():
    return filter(
        lambda x: x is not None,
        [load_command(name) for name in command_names()]
    )


def load_command(name):
    full_name = 'opbeatcli.commands.%s' % name

    try:
        if full_name not in sys.modules:
            __import__(full_name)
    except ImportError, ex:
        print ex
    else:
        return sys.modules[full_name].command


def command_names():
    names = set(
        pkg[1] for pkg in
        walk_packages(path=opbeatcli.commands.__path__)
    )
    return list(names)


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
            usage=self.usage,
            name=self.name
        )

        self.parser.set_defaults(func=self.run_first)

        self.add_args()

    def add_args(self):
        pass

    def run_first(self, args, logger):
        self.logger = logger
        self.run(args)

    def run(self, args):
        raise NotImplemented
