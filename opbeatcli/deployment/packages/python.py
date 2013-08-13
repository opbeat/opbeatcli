"""
Python requirements and their discovery.

http://www.pip-installer.org/en/latest/requirements.html#the-requirements-file-format

"""
from opbeatcli.exceptions import DependencyParseError
from opbeatcli.compat import urlsplit
from .base import BaseDependencyCollector, BaseDependency
from .types import PYTHON_PACKAGE
from ..vcs import VCS, VCS_NAME_MAP


def parse_editable(uri):
    """
    <remote_url>@<rev>#egg=<name>

    See `pip.vcs.<backend>.<Backend>.get_src_requirement()`.

    """

    bits = urlsplit(uri)

    remove_scheme = False

    if not bits.scheme:
        # git+git@github.com:opbeat/opbeatcli.git@a2794#egg=opbeatcli-dev
        assert uri.startswith('git+')
        uri = 'git://' + uri[4:]
        bits = urlsplit(uri)
        remove_scheme = True

    remote_url = uri.rsplit('@', 1)[0]

    if '+' in bits.scheme:
        vcs_type, remote_url = remote_url.split('+', 1)
    else:
        assert bits.scheme == 'git', bits.scheme
        vcs_type = 'git'

    if '#' in bits.path:
        # Python 2.6 sometimes fails to parse fragment.
        # /ipython/ipython.git@rev#egg=ipython-dev
        rev, name = bits.path.split('@')[1].split('#egg=')
    else:
        name = bits.fragment.split('=', 1)[1]
        rev = bits.path.split('@')[1]

    if remove_scheme:
        remote_url = remote_url[len(bits.scheme) + 3:]

    version = None
    if vcs_type in ['git', 'hg', 'bzr']:
        # There is no version as such, but each of the VCS backends appends
        # some VCS info to the name (or just '-dev'). SVN is tricky, so we
        # don't parse the name there.
        name, version = name.rsplit('-', 1)

    parsed = {
        'name': name,
        'version': version,
        'vcs': {
            'vcs_type': VCS_NAME_MAP[vcs_type],
            'rev': rev,
            'remote_url': remote_url,
        }
    }

    assert all([parsed['name'],
                parsed['vcs']['rev'],
                parsed['vcs']['vcs_type'],
                parsed['vcs']['remote_url']]), parsed

    return parsed


class PythonCollector(BaseDependencyCollector):

    default_commands = [
        'pip freeze'
    ]

    def parse(self, output):
        # Note: we only parse `pip freeze' output, not raw dependency specs.
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('-e'):
                try:
                    kwargs = parse_editable(line.split(None, 1)[1])
                except Exception:
                    msg = 'Unparseable editable requirement: %r' % str(line)
                    self.logger.debug(msg, exc_info=True)
                    raise DependencyParseError(msg)

                kwargs['vcs'] = VCS(**kwargs['vcs'])
                yield PythonDependency(**kwargs)

            else:
                try:
                    name, version = line.split('==')
                except ValueError:
                    raise DependencyParseError(line)

                yield PythonDependency(name=name, version=version)


class PythonDependency(BaseDependency):

    package_type = PYTHON_PACKAGE

