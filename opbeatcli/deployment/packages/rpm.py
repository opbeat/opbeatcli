from opbeatcli.exceptions import DependencyParseError
from .base import BaseDependency, DependencyCollector
from .types import RPM_PACKAGE


class RPMCollector(DependencyCollector):

    default_commands = [
        r"rpm --query --all --queryformat='%{NAME} %{VERSION}%{RELEASE}\n'"
    ]

    def parse(self, output):
        for line in output.splitlines():
            try:
                name, version = line.split()
            except ValueError:
                raise DependencyParseError(line)
            yield RPMDependency(name=name, version=version)


class RPMDependency(BaseDependency):
    package_type = RPM_PACKAGE
