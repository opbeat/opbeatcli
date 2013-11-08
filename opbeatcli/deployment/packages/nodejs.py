import json

from opbeatcli.exceptions import DependencyParseError
from .base import BaseDependency, BaseDependencyCollector
from .types import NODE_PACKAGE


class NodeCollector(BaseDependencyCollector):
    default_commands = [
        'npm --json --global list',
        'npm --json --local list',
    ]

    def is_fatal_error(self, exit_status, stdout, stderr):
        """
        Use `npm list` output as long as it is parseable JSON regardless
        of the error exit status code.

        Sometimes `npm` exits with `1` and a message like::

            npm ERR! missing: coffee-script@~1.6.3, required by
                        coffee-script-brunch@1.7.2
            npm ERR! not ok code 0

        It's basically just a warning so treat it as such.

        """
        if exit_status == 1:
            try:
                data = json.loads(stdout)
            except ValueError:
                pass
            else:
                if isinstance(data, dict):
                    self.logger.warning(stderr)
                    return False
        return True

    def parse(self, output):
        try:
            data = json.loads(output)
        except ValueError as e:
            raise DependencyParseError(str(e))

        for name, dep_data in data.get('dependencies', {}).items():
            yield NodeDependency(name=name, version=dep_data['version'])


class NodeDependency(BaseDependency):
    package_type = NODE_PACKAGE
