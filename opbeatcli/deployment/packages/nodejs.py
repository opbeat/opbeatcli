import json

from .base import BaseDependency, DependencyCollector
from .types import NODE_PACKAGE


class NodeCollector(DependencyCollector):
    default_commands = [
        'npm --json --global list',
        'npm --json --local list',
    ]

    def parse(self, output):
        data = json.loads(output)
        for name, dep_data in data.get('dependencies', {}).items():
            yield NodeDependency(name=name, version=dep_data['version'])


class NodeDependency(BaseDependency):
    package_type = NODE_PACKAGE
