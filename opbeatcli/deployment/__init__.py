from itertools import chain
from opbeatcli.deployment import serialize

from .packages import Component, PYTHON_PACKAGE, NODE_PACKAGE, RUBY_PACKAGE
from .stacks import python, nodejs, ruby


DEPENDENCY_COLLECTORS = {
    PYTHON_PACKAGE: python.collect_dependencies,
    NODE_PACKAGE: nodejs.collect_dependencies,
    RUBY_PACKAGE: ruby.collect_dependencies,
}


def get_deployment_data(
        local_hostname,
        repo_specs,
        local_repo_specs,
        collect_dependency_types):
    """"""
    return serialize.deployment(
        local_hostname=local_hostname,
        packages=chain(
            collect_dependencies(collect_dependency_types),
            get_components(repo_specs, local_repo_specs)
        ),
    )


def collect_dependencies(for_types):
    for dep_type in for_types:
        for dependency in DEPENDENCY_COLLECTORS[dep_type]():
            yield dependency


def get_components(repo_specs, local_repo_specs):

    for repo_spec in repo_specs:
        yield Component.from_repo_spec(repo_spec)

    for local_repo_spec in local_repo_specs:
        yield Component.from_local_repo_spec(local_repo_spec)
