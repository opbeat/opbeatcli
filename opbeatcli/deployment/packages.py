"""
Models representing packages.

"""
from __future__ import absolute_import
import os
import re

from opbeatcli.exceptions import InvalidArgumentError
from .vcs import VCSInfo, find_vcs_root


PYTHON_PACKAGE = 'python'
RUBY_PACKAGE = 'ruby'
NODE_PACKAGE = 'nodejs'
COMPONENT_PACKAGE = 'repository'


PACKAGE_TYPES = set([
    COMPONENT_PACKAGE,
    PYTHON_PACKAGE,
    # RUBY_PACKAGE,
    # NODE_PACKAGE,
])


class BasePackage(object):
    """
    Any installed package that the user wants to record for a deployment.

    It can be an app component, dependency, requirement, ...

    """

    package_type = None

    def __init__(self, path, name=None, version=None):
        assert self.package_type in PACKAGE_TYPES
        self.path = os.path.abspath(path)
        self.name = name or os.path.basename(self.path.rstrip(os.pathsep))
        if not self.name:
            # Edge case: happens when `name` bit specified and `path` is '/'.
            raise InvalidArgumentError('Missing package name')
        self.version = version

    def get_vcs_info(self):
        return VCSInfo.from_path(self.path)

    def to_json(self):
        data = {
            'module': {
                'name': self.name,
                'module_type': self.package_type,
            },
            'version': self.version
        }
        vcs_info = self.get_vcs_info()
        if vcs_info:
            data['vcs'] = vcs_info.to_json()

        return data

    def __repr__(self):
        return (
            '{cls}(path={path!r}, name={name!r}, version={version!r})'
            .format(
                cls=type(self).__name__,
                **self.__dict__
            )
        )


class BaseRequirement(BasePackage):
    """
    A piece of software installed along side and needed by the app, but not
    a component of the app.

    Each stack defines its own subclass.

    Nothing directly here for now.

    """


class Component(BasePackage):
    """
    A code component of the app being deployed (--repo for the user).

    """
    package_type = COMPONENT_PACKAGE

    REPO_SPEC_RE = re.compile(
        """
        ^
        (?P<path>[^:@]+)
        (:(?P<name>[^:@]+))?
        (@(?P<version>[^:@]+))?
        $
        """,
        re.VERBOSE
    )

    def get_vcs_info(self):
        vcs_root = find_vcs_root(self.path)
        if vcs_root:
            return VCSInfo.from_path(vcs_root)

    @classmethod
    def from_repo_spec(cls, spec):
        match = cls.REPO_SPEC_RE.match(spec)
        if not match:
            raise InvalidArgumentError('Invalid repo spec: %r' % spec)
        kwargs = match.groupdict()
        return cls(**kwargs)
