from .base import BaseDependency, DependencyCollector
from .types import DEB_PACKAGE


class DebCollector(DependencyCollector):

    default_commands = [
        r"dpkg-query --show --showformat='${package} ${version}\n'"
    ]

    def parse(self, output):
        for line in output.splitlines():
            name, version = line.split()
            yield DebDependency(name=name, version=version)


class DebDependency(BaseDependency):
    package_type = DEB_PACKAGE
