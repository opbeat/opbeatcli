"""
Serialization of objects to the data format required by the API.

This implementation is for version 1 of the API.

"""


def deployment(local_hostname, packages):
    return {
        'releases': [package(pkg) for pkg in packages],
        'machines': {'hostname': local_hostname},
    }


def package(pkg):
    """
    :type pkg: BasePackage
    """
    data = {
        'module': {
            'name': pkg.name,
            'module_type': pkg.package_type,
        },
        'version': pkg.version
    }
    if pkg.vcs_info:
        data['vcs'] = {
            'type': pkg.vcs_info.vcs_type,
            'revision': pkg.vcs_info.rev,
            'repository': pkg.vcs_info.remote_url,
            # 'branch': self.branch,
        }
    return data
