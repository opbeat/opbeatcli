from ..packages import BaseDependency, DEB_PACKAGE
from .base import DependencyCollector


class DebCollector(DependencyCollector):

    default_command = \
        r"dpkg-query --show --showformat='${package} ${version}\n'"

    def parse(self, output):
        for line in output.splitlines():
            name, version = line.split()
            yield DebDependency(name=name, version=version)


class DebDependency(BaseDependency):
    package_type = DEB_PACKAGE
