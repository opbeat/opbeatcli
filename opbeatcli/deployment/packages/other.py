from .base import BaseDependency
from .types import OTHER_PACKAGE

# No collector, need to be specified via --dependency.


class OtherDependency(BaseDependency):

    package_type = OTHER_PACKAGE
