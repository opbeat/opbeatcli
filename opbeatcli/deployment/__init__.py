from itertools import chain

from .packages import Component
from opbeatcli.deployment.stacks import python


def get_deployment_data(local_hostname, repo_specs, local_repo_specs):
    """"""

    packages = chain(
        get_requirements(),
        get_components(repo_specs, local_repo_specs)
    )

    return {
        'releases': [
            package.to_json() for package in packages
        ],
        'machines': [
            {
                'hostname': local_hostname
            }
        ],
    }


def get_requirements():
    return python.get_installed_requirements()


def get_components(repo_specs, local_repo_specs):

    for repo_spec in repo_specs:
        yield Component.from_repo_spec(repo_spec)

    for local_repo_spec in local_repo_specs:
        yield Component.from_local_repo_spec(local_repo_spec)
