import os

from pip.vcs import vcs
from opbeatcli.exceptions import InvalidArgumentError

from opbeatcli.utils.ssh_config import SSHConfig

try:
    # noinspection PyCompatibility
    from urllib.parse import urlsplit, urlunsplit
except ImportError:  # Python < 3.0
    # noinspection PyCompatibility
    from urlparse import urlsplit, urlunsplit


VCS_NAME_MAP = {
    'git': 'git',
    'hg': 'mercurial',
    'svn': 'subversion'
}


def find_vcs_root(path):
    """Walk up the hierarchy and return the first VCS root found."""
    while path and path != '/':
        if is_vcs_root(path):
            return path
        path = os.path.split(path)[0]


def is_vcs_root(path):
    return vcs.get_backend_name(path) is not None


class VCSInfo(object):

    def __init__(self, rev, vcs_type=None, branch=None, remote_url=None):

        types = list(VCS_NAME_MAP.values())

        if vcs_type not in types:
            raise InvalidArgumentError(
                'invalid VCS type %r, it has to be one of %s' % (
                    vcs_type,
                    ', '.join(types),
                )
            )
        self.vcs_type = vcs_type
        self.rev = rev
        self.branch = branch
        self.remote_url = remote_url

    def __repr__(self):
        return (
            '{cls}(rev={rev!r}, vcs_type={vcs_type!r},'
            ' branch={branch!r}, remote_url={remote_url!r})'
            .format(
                cls=type(self).__name__,
                **self.__dict__
            )
        )

    def to_json(self):
        return {
            'type': self.vcs_type,
            'revision': self.rev,
            'repository': self.remote_url,
            # 'branch': self.branch,
        }

    @classmethod
    def from_path(cls, path):
        backend_class = vcs.get_backend_from_location(path)
        if backend_class:
            backend = backend_class(path)
            return VCSInfo(
                vcs_type=VCS_NAME_MAP[backend.name],
                rev=backend.get_revision(path),
                remote_url=expand_ssh_host_alias(backend.get_url(path)),
                # TODO: branch support.
                branch=None,
            )


def expand_ssh_host_alias(url, config=None):
    """Return ``url`` with the real host name if it has an SSH alias."""
    config = config or _get_ssh_config()

    if config:
        DUMMY_SCHEME = 'opbeat-dummy://'
        parts = urlsplit(url)
        if not parts.scheme:
            # If scheme is not present in the URL, the whole URL
            # gets interpretted as path, and we don't like that.
            parts = urlsplit(DUMMY_SCHEME + url)

        host_alias = parts.netloc.split('@')[-1].split(':')[0]
        host_expanded = config.lookup(host_alias).get('hostname')
        if host_expanded:
            netloc = parts.netloc.replace(host_alias, host_expanded, 1)
            parts = list(parts)  # [scheme, netloc, path, query, fragment]
            parts[1] = netloc
            url = urlunsplit(parts)
            if url.startswith(DUMMY_SCHEME):
                url = url[len(DUMMY_SCHEME):]

    return url


def _get_ssh_config(path='~/.ssh/config'):
    """Return a parsed ``SSHConfig``, if config file present and parsable."""
    try:
        with open(os.path.expanduser(path), 'r') as f:
            config = SSHConfig()
            try:
                # noinspection PyTypeChecker
                config.parse(f)
                return config
            except Exception:
                pass
    except IOError:
        pass
