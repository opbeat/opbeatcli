from .base import BaseDependency, DependencyCollector
from .types import RPM_PACKAGE


class RPMCollector(DependencyCollector):

    default_command = \
        r"rpm --query --all --queryformat='%{NAME} %{VERSION}%{RELEASE}\n'"

    def parse(self, output):
        for line in output.splitlines():
            name, version = line.split()
            yield RPMDependency(name=name, version=version)


class RPMDependency(BaseDependency):
    package_type = RPM_PACKAGE
