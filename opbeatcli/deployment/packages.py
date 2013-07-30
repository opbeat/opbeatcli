"""
Models representing packages.

"""
from __future__ import absolute_import
import os

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

    def __init__(self, name, version=None, vcs_info=None):
        assert self.package_type in PACKAGE_TYPES
        self.name = name
        self.version = version
        self.vcs_info = vcs_info

    def to_json(self):
        data = {
            'module': {
                'name': self.name,
                'module_type': self.package_type,
            },
            'version': self.version
        }
        if self.vcs_info:
            data['vcs'] = self.vcs_info.to_json()

        return data

    def __repr__(self):
        return (
            '{cls}(name={name!r}, version={version!r})'
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
    A code component of the app being deployed.

    (--repo / --local-repo for the user).

    """
    package_type = COMPONENT_PACKAGE

    @classmethod
    def from_repo_spec(cls, spec):
        vcs = {
            'vcs_type': spec.pop('vcs'),
            'branch': spec.pop('branch'),
            'rev': spec.pop('rev'),
            'remote_url': spec.pop('remote_url'),
        }

        vcs_info = None
        if not spec['version'] and not (vcs['vcs_type'] and vcs['rev']):
            raise InvalidArgumentError(
                '--repo has to have at least either "version",'
                ' or both "vcs" and "rev"'
            )

        if any(vcs.values()):
            vcs_info = VCSInfo(**vcs)

        return cls(vcs_info=vcs_info, **spec)

    @classmethod
    def from_local_repo_spec(cls, spec):
        path = os.path.abspath(os.path.expanduser(spec.pop('path')))
        if not os.path.isdir(path):
            raise InvalidArgumentError(
                'Local repository path does not exist: %r' % path
            )

        vcs_root = find_vcs_root(path)
        if not vcs_root:
            raise InvalidArgumentError(
                'No VCS root found for the local repository: %r' % path
            )

        vcs_info = VCSInfo.from_path(vcs_root)
        name = spec.pop('name') or os.path.basename(path.rstrip(os.path.sep))
        return cls(vcs_info=vcs_info, name=name, **spec)
