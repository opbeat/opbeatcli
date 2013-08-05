from operator import attrgetter
from itertools import chain, groupby

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

    get_type = attrgetter('key')
    get_command = attrgetter('value')

    groups = groupby(sorted(for_types, key=get_type), key=get_type)

    for dep_type, group in groups:

        try:
            collector_class = DEPENDENCY_COLLECTORS[dep_type]
        except KeyError:
            raise InvalidArgumentError(
                'Unknown dependency type to collect: %r' % dep_type
            )

        custom_commands = map(get_command, group)

        if len(custom_commands) != len(set(custom_commands)):
            raise InvalidArgumentError(
                'Duplicate dependency type: %s' % dep_type
            )

        commands = []
        for custom_command in custom_commands:
            if custom_command is None:
                commands.extend(collector_class.default_commands)
            else:
                commands.append(custom_command)

        collector = collector_class(custom_commands=commands)

        try:
            for dep in collector.collect():
                yield dep
        except CommandNotFoundError:
            if types_specified:
                # We can ignore this error unless the user explicitely asked
                # for this type (and also possibly supplied a custom command).
                raise
