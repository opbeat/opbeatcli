from . import python, nodejs, ruby, deb
from .. import packages


DEPENDENCY_COLLECTORS = {
    packages.PYTHON_PACKAGE: python.PythonCollector,
    packages.NODE_PACKAGE: nodejs.NodeCollector,
    packages.RUBY_PACKAGE: ruby.RubyCollector,
    packages.DEB_PACKAGE: deb.DebCollector,
}
