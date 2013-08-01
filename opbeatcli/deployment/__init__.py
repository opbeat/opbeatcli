from itertools import chain

from opbeatcli.deployment import serialize
from opbeatcli.exceptions import InvalidArgumentError, CommandNotFoundError
from .packages import Component
from .stacks import DEPENDENCY_COLLECTORS


def get_deployment_data(
        local_hostname,
        repo_specs,
        local_repo_specs,
        dependency_specs,
        collect_dep_types,
        collect_dep_types_specified
    ):
    """Return actual deployment data to be POSTed to the API"""
    return serialize.deployment(
        local_hostname=local_hostname,
        packages=chain(
            _collect_dependencies(
                collect_dep_types,
                collect_dep_types_specified,
            ),
            _get_components(repo_specs, local_repo_specs)
        ),
    )


def _collect_dependencies(for_types, types_specified):
    for dep_type in for_types:

        if ':' not in dep_type:
            custom_command = None
        else:
            dep_type, custom_command = dep_type.split(':', 1)

        if dep_type not in DEPENDENCY_COLLECTORS:
            raise InvalidArgumentError(
                'Unknown dependency type: %r' % dep_type
            )

        collector_class = DEPENDENCY_COLLECTORS[dep_type]
        collector = collector_class(custom_command=custom_command)

        try:
            for dep in collector.collect():
                yield dep
        except CommandNotFoundError:
            if types_specified:
                # We can ignore this error unless the user explicitely asked
                # for this type (and also possibly supplied a custom command).
                raise


def _get_components(repo_specs, local_repo_specs):

    for repo_spec in repo_specs:
        yield Component.from_repo_spec(repo_spec)

    for local_repo_spec in local_repo_specs:
        yield Component.from_local_repo_spec(local_repo_spec)
