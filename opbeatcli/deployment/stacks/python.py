"""
Python requirements and their discovery.

"""
from pip.util import get_installed_distributions

from ..packages import BaseRequirement, PYTHON_PACKAGE


def get_installed_requirements():
    """Installed Python requirements according to `pip'"""
    for distribution in get_installed_distributions():
        yield PythonRequirement.from_distribution(distribution)


class PythonRequirement(BaseRequirement):

    package_type = PYTHON_PACKAGE

    @classmethod
    def from_distribution(cls, distribution):
        """
        :type distribution: pkg_resources.Distribution

        """
        version = distribution.version if distribution.has_version() else None
        return cls(
            name=distribution.key,
            path=distribution.location,
            version=version,
        )
