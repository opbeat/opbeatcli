"""
Python requirements and their discovery.

"""
from pip.util import get_installed_distributions

from ..packages import BaseDependency, PYTHON_PACKAGE
from ..vcs import VCSInfo


def collect_dependencies():
    """Installed Python requirements according to `pip'"""
    for distribution in get_installed_distributions():
        yield PythonDependency.from_distribution(distribution)


class PythonDependency(BaseDependency):

    package_type = PYTHON_PACKAGE

    @classmethod
    def from_distribution(cls, distribution):
        """
        :type distribution: pkg_resources.Distribution

        """
        version = distribution.version if distribution.has_version() else None
        return cls(
            name=distribution.key,
            version=version,
            vcs_info=VCSInfo.from_path(distribution.location),
        )
