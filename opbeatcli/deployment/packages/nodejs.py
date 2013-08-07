import json

from opbeatcli.exceptions import DependencyParseError
from .base import BaseDependency, BaseDependencyCollector
from .types import NODE_PACKAGE


class NodeCollector(BaseDependencyCollector):
    default_commands = [
        'npm --json --global list',
        'npm --json --local list',
    ]

    def parse(self, output):
        try:
            data = json.loads(output)
        except ValueError as e:
            raise DependencyParseError(str(e))

        for name, dep_data in data.get('dependencies', {}).items():
            yield NodeDependency(name=name, version=dep_data['version'])


class NodeDependency(BaseDependency):
    package_type = NODE_PACKAGE
