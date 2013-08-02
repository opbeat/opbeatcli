from itertools import chain

from opbeatcli.deployment import serialize
from opbeatcli.exceptions import InvalidArgumentError, CommandNotFoundError
from .packages.base import BaseDependency
from .packages.component import Component
from .packages import DEPENDENCY_COLLECTORS


def get_deployment_data(local_hostname, component_specs, dependency_specs,
                        collect_dep_types, collect_dep_types_specified):
    """Return actual deployment data to be POSTed to the API"""

    packages = chain(
        (Component.from_spec(spec) for spec in component_specs),
        (BaseDependency.from_spec(spec) for spec in dependency_specs),
        _collect_dependencies(collect_dep_types, collect_dep_types_specified),
    )

    return serialize.deployment(
        local_hostname=local_hostname,
        packages=packages,
    )


def _collect_dependencies(for_types, types_specified):
    for dep_type in for_types:

        if ':' not in dep_type:
            custom_command = None
        else:
            dep_type, custom_command = dep_type.split(':', 1)

        try:
            collector_class = DEPENDENCY_COLLECTORS[dep_type]
        except KeyError:
            raise InvalidArgumentError(
                'Unknown dependency type to collect: %r' % dep_type
            )

        collector = collector_class(custom_command=custom_command)

        try:
            for dep in collector.collect():
                yield dep
        except CommandNotFoundError:
            if types_specified:
                # We can ignore this error unless the user explicitely asked
                # for this type (and also possibly supplied a custom command).
                raise
