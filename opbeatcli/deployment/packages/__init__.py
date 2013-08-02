from . import types
from . import python, nodejs, ruby, deb, rpm, other


DEPENDENCY_COLLECTORS = {
    types.PYTHON_PACKAGE: python.PythonCollector,
    types.NODE_PACKAGE: nodejs.NodeCollector,
    types.RUBY_PACKAGE: ruby.RubyCollector,
    types.DEB_PACKAGE: deb.DebCollector,
    types.RPM_PACKAGE: rpm.RPMCollector,
}


DEPENDENCIES_BY_TYPE = {
    types.PYTHON_PACKAGE: python.PythonDependency,
    types.NODE_PACKAGE: nodejs.NodeDependency,
    types.RUBY_PACKAGE: ruby.RubyDependency,
    types.DEB_PACKAGE: deb.DebDependency,
    types.RPM_PACKAGE: rpm.RPMDependency,
    types.OTHER_PACKAGE: other.OtherDependency,
}
