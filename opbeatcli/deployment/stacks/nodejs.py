import json
import subprocess

from ..packages import BaseDependency, NODE_PACKAGE


def collect_dependencies():
    output = subprocess.check_output('npm --global --json list', shell=True)
    data = json.loads(output)
    for name, dep_data in data['dependencies'].items():
        yield NodeDependency(name=name, version=dep_data['version'])


class NodeDependency(BaseDependency):

    package_type = NODE_PACKAGE
