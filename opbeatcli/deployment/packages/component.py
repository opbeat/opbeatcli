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

        # Try to fetch VCS info from path if no VCS attributes specified.
        vcs_from_path = None
        vcs_root = find_vcs_root(path)
        if not kwargs['vcs'] and vcs_root:
            vcs_from_path = VCS.from_path(vcs_root)

        if vcs_from_path:
            kwargs['vcs'] = vcs_from_path
        elif not (kwargs['version'] or (kwargs['vcs'] and kwargs['vcs'].rev)):
            # Missing version/revision info.

            if not kwargs['vcs']:
                # No VCS attributes specified and path is not a VCS repo.
                message = (
                    'The directory is not a VCS repository, therefore at least'
                    ' "version:<version>" or  "rev:<vcs-revision>" is'
                    ' required.'
                )
            elif vcs_root:
                # Some VCS attributes specified but version/rev is missing,
                # even though the path is a VCS repo.
                message = (
                    '"version:<version>" or "rev:<vcs-revision>" is required.'
                    '\nNote: the directory {path!r} is a VCS repository,'
                    ' therefore it is unnecessary to specify any VCS'
                    ' attributes manually. They are filled in'
                    ' automatically if none specified.'
                )
            else:
                # Some VCS attributes specified and path isn't a VCS repo.
                message = (
                    '"version:<version>" or "rev:<vcs-revision>" is required.'
                )

            message = '--component: path:{path!r}: ' + message
            raise InvalidArgumentError(message.format(**kwargs))

        return kwargs
