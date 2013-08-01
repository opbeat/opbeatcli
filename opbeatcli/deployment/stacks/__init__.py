from . import python, nodejs, ruby, deb, rpm
from .. import packages


DEPENDENCY_COLLECTORS = {
    packages.PYTHON_PACKAGE: python.PythonCollector,
    packages.NODE_PACKAGE: nodejs.NodeCollector,
    packages.RUBY_PACKAGE: ruby.RubyCollector,
    packages.DEB_PACKAGE: deb.DebCollector,
    packages.RPM_PACKAGE: rpm.RPMCollector,
}


DEPENDENCIES_BY_TYPE = {
    packages.PYTHON_PACKAGE: python.PythonDependency,
    packages.NODE_PACKAGE: nodejs.NodeDependency,
    packages.RUBY_PACKAGE: ruby.RubyDependency,
    packages.DEB_PACKAGE: deb.DebDependency,
    packages.RPM_PACKAGE: rpm.RPMDependency,
}

