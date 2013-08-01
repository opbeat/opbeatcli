from ..packages import BaseDependency, RUBY_PACKAGE
from .base import DependencyCollector


class RubyCollector(DependencyCollector):

    default_command = 'gem list'

    def parse(self, output):
        for line in output.strip().splitlines():
            # eg. "arel (3.0.2, 2.1.1, 2.0.10, 2.0.9)"
            i = line.index(' ')
            name = line[:i]
            versions = line[i+2:-1]
            for version in versions.split(', '):
                yield RubyDependency(name=name, version=version)


class RubyDependency(BaseDependency):

    package_type = RUBY_PACKAGE
