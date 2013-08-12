"""
Serialization of objects to the data format required by the API.

This implementation is for version 1 of the API.

"""
from .packages.component import Component


LEGACY_COMPONENT_PACKAGE = 'repository'


def deployment(local_hostname, packages):
    return {
        'releases': [package(pkg) for pkg in packages],
        'machines': [{'hostname': local_hostname}],
    }


def package(pkg):
    """
    :type pkg: BasePackage

    """

    def drop_none_keys(dct):
        return dict(
            (key, (drop_none_keys(value)
                   if isinstance(value, dict)
                   else value))
            for key, value in dct.items()
            if value is not None
        )

    data = {
        'module': {
            'name': pkg.name,
            'type': pkg.package_type,
        },
        'version': pkg.version
    }
    if isinstance(pkg, Component):
        data['path'] = pkg.path
        data['module']['type'] = LEGACY_COMPONENT_PACKAGE

    if pkg.vcs:
        data['vcs'] = {
            'type': pkg.vcs.vcs_type,
            'revision': pkg.vcs.rev,
            'repository': pkg.vcs.remote_url,
            'branch': pkg.vcs.branch,
        }

    return drop_none_keys(data)
