"""
Python requirements and their discovery.

http://www.pip-installer.org/en/latest/requirements.html#the-requirements-file-format

"""
import requirements

from .base import DependencyCollector, BaseDependency
from .types import PYTHON_PACKAGE
from ..vcs import VCS


class PythonCollector(DependencyCollector):

    default_commands = [
        'pip freeze'
    ]

    def parse(self, output):
        for req in requirements.parse(output):
            # {'extras': [], 'name': 'redis', 'specs': [('==', '2.6.2')]}
            try:
                version = req['specs'][0][1]
            except (KeyError, IndexError):
                version = None

            if 'vcs' not in req:
                vcs = None
            else:
                uri = req['uri']
                at = uri.rindex('@')
                # FIXME: rev can also be a tag or branch
                remote_url, rev = uri[:at], uri[at + 1:]
                vcs = VCS(
                    vcs_type=req['vcs'],
                    remote_url=remote_url,
                    rev=rev
                )

            yield PythonDependency(
                name=req['name'],
                version=version,
                vcs=vcs,
            )


class PythonDependency(BaseDependency):

    package_type = PYTHON_PACKAGE
