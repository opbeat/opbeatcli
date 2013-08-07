import os

from opbeatcli.exceptions import InvalidArgumentError
from ..vcs import VCS, find_vcs_root
from .base import BasePackage
from .types import COMPONENT_PACKAGE


class Component(BasePackage):
    """
    A code component of the app being deployed.

    """
    package_type = COMPONENT_PACKAGE

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(Component, self).__init__(*args, **kwargs)

    def __repr__(self):
        return (
            '{cls}(path={path!r}, name={name!r},'
            ' version={version!r}, vcs={vcs!r})'
            .format(
                cls=type(self).__name__,
                **self.__dict__
            )
        )

    @classmethod
    def spec_to_kwargs(cls, spec):
        # Component specs have a path which can be used to fill in name
        # and VCS attributes.

        kwargs = super(Component, cls).spec_to_kwargs(spec)

        path = os.path.abspath(os.path.expanduser(spec['path']))
        kwargs['path'] = path
        if not kwargs['name']:
            kwargs['name'] = os.path.basename(path.rstrip(os.path.sep))

        vcs_root = find_vcs_root(path)
        if vcs_root:
            kwargs['vcs'] = VCS.from_path(vcs_root)

        if not kwargs['version'] and not (kwargs['vcs'] and kwargs['vcs'].rev):
            raise InvalidArgumentError(
                '--component has to have at least either "version" or "rev"'
            )

        return kwargs

