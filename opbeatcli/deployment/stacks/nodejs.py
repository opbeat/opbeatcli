# coding:utf8
import json

from ..packages import BaseDependency, NODE_PACKAGE
from .base import DependencyCollector


# npm output looks like the following and we only take the root packages.
# $ npm --global list
# /usr/local/share/npm/lib
# ├─┬ bower@0.9.2
# │ ├── abbrev@1.0.4
# │ ├── archy@0.0.2
# │ ├── async@0.2.8
# │ ├── colors@0.6.0-1
# │ ├─┬ fstream@0.1.22
# │ │ ├── graceful-fs@1.2.1
# │ │ └── inherits@1.0.0
# │ ├─┬ glob@3.1.21
# │ │ ├── graceful-fs@1.2.1
# │ │ ├── inherits@1.0.0
# │ │ └─┬ minimatch@0.2.12
# │ │   ├── lru-cache@2.3.0
# │ │   └── sigmund@1.0.0

# $ npm list
# /
# └── (empty)

class NodeCollector(DependencyCollector):

    default_command = 'npm --global list'

    def parse(self, output):

        root_node_prefix = u'├'
        for line in output.splitlines():
            if line.startswith(root_node_prefix) and '@' in line:
                # eg. "├─┬ bower@0.9.2"
                try:
                    name, version = line.split()[1].split('@')
                except (IndexError, ValueError):
                    raise ValueError('Invalid npm output: %r' % line)

                yield NodeDependency(name=name, version=version)


class NodeDependency(BaseDependency):
    package_type = NODE_PACKAGE
