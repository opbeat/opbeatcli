import sys
from subprocess import Popen, PIPE

from opbeatcli.log import logger
from opbeatcli.exceptions import CommandError, CommandNotFoundError


COMMAND_NOT_FOUND = 127


class DependencyCollector(object):

    default_command = None
    custom_command = None

    def __init__(self, custom_command=None):
        self.custom_command = custom_command

    def run_command(self):
        command = self.custom_command or self.default_command
        process = Popen(command, shell=True, stdout=PIPE)
        out, err = process.communicate()
        ret = process.poll()

        if ret:
            if ret == COMMAND_NOT_FOUND:
                raise CommandNotFoundError()
            raise CommandError()

        return out.decode(sys.stdout.encoding)

    def parse(self, output):
        """Parse command ``output`` nad return a ``list`` of dependencies."""
        return []

    def collect(self):
        """Return a list of dependencies."""
        return self.parse(self.run_command())
