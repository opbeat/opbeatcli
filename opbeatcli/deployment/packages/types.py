"""
Definition of package types.

There are two primary types of packages:

    1. Components (COMPONENT_PACKAGE)
    2. Dependencies (All the other ones).

"""
COMPONENT_PACKAGE = 'component'
OTHER_PACKAGE = 'other'
PYTHON_PACKAGE = 'python'
RUBY_PACKAGE = 'ruby'
NODE_PACKAGE = 'nodejs'
DEB_PACKAGE = 'deb'
RPM_PACKAGE = 'rpm'


PACKAGE_TYPES = set([
    COMPONENT_PACKAGE,
    PYTHON_PACKAGE,
    NODE_PACKAGE,
    RUBY_PACKAGE,
    DEB_PACKAGE,
    RPM_PACKAGE,
    OTHER_PACKAGE,
])
