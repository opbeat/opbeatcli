import re

from opbeatcli.exceptions import DependencyParseError
from .base import BaseDependencyCollector, BaseDependency
from .types import RUBY_PACKAGE


# eg. "arel (3.0.2, 2.1.1, 2.0.10, 2.0.9)"
GEM_RE = re.compile('^[^\s]+ \([^\s]+(, [^\s]+)*\)$')


class RubyCollector(BaseDependencyCollector):

    default_commands = [
        'gem list'
    ]

    def parse(self, output):
        for line in output.strip().splitlines():
            if not GEM_RE.match(line):
                raise DependencyParseError(line)
            i = line.index(' ')
            name = line[:i]
            versions = line[i+2:-1]
            for version in versions.split(', '):
                yield RubyDependency(name=name, version=version)


class RubyDependency(BaseDependency):
    package_type = RUBY_PACKAGE
