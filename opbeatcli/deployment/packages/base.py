from __future__ import absolute_import
from subprocess import Popen, PIPE

from opbeatcli.exceptions import InvalidArgumentError
from opbeatcli.log import logger
from opbeatcli.exceptions import CommandError, CommandNotFoundError
from ..vcs import VCS
from .types import PACKAGE_TYPES


class BasePackage(object):
    """
    Any installed package that the user wants to record for a deployment.

    It can be an app component, dependency, requirement, ...

    """

    package_type = None

    def __init__(self, name, version=None, vcs=None):
        assert self.package_type in PACKAGE_TYPES
        self.name = name
        self.version = version
        self.vcs = vcs

    def __repr__(self):
        return (
            '{cls}(name={name!r}, version={version!r})'
            .format(
                cls=type(self).__name__,
                **self.__dict__
            )
        )

    @classmethod
    def spec_to_kwargs(cls, spec):
        """Process a validated spec and prepare common keyword arguments.

        :type spec: dict

        """
        kwargs = {
            'name': spec['name'],
            'version': spec['version'],
            'vcs': None
        }
        vcs_kwargs = {
            'vcs_type': spec.pop('vcs'),
            'branch': spec.pop('branch'),
            'rev': spec.pop('rev'),
            'remote_url': spec.pop('remote_url'),
        }
        if any(vcs_kwargs.values()):
            kwargs['vcs'] = VCS(**vcs_kwargs)

        return kwargs

    @classmethod
    def from_spec(cls, spec):
        return cls(**cls.spec_to_kwargs(spec))


class BaseDependency(BasePackage):
    """
    A piece of software installed along side and needed by the app, but not
    a component of the app.

    Each stack defines its own subclass.

    """
    @classmethod
    def from_spec(cls, spec):
        # Dependency specs have a type which determines which dependency class
        # to instantiate for it.
        from . import DEPENDENCIES_BY_TYPE

        kwargs = cls.spec_to_kwargs(spec)
        package_type = spec['type']

        if not kwargs['version'] and not (kwargs['vcs'] and kwargs['vcs'].rev):
            raise InvalidArgumentError(
                '--dependency has to have at least either "version" or "rev"'
            )
        package_class = DEPENDENCIES_BY_TYPE[package_type]
        return package_class(**kwargs)


class DependencyCollector(object):

    default_commands = []
    custom_commands = None

    def __init__(self, custom_commands=None):
        self.custom_commands = custom_commands
        self.logger = logger.getChild(type(self).__name__)

    def run_command(self, command):
        COMMAND_NOT_FOUND = 127
        self.logger.info(command)
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        ret = process.poll()

        if ret:
            if ret == COMMAND_NOT_FOUND:
                raise CommandNotFoundError(err)
            raise CommandError(err)

        # FIXME: might be another encoding.
        return out.strip().decode('utf8')

    def parse(self, output):
        """Parse command ``output`` nad return a ``list`` of dependencies."""
        return []

    def collect(self):
        """Return a list of dependencies."""
        commands = self.custom_commands or self.default_commands
        for command in commands:
            print command
            for dep in self.parse(self.run_command(command)):
                yield dep
