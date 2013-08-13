import os
import subprocess

from pip.vcs import vcs

from opbeatcli.exceptions import InvalidArgumentError
from opbeatcli.utils.ssh_config import SSHConfig

try:
    #noinspection PyCompatibility
    from urllib.parse import urlsplit, urlunsplit
except ImportError:  # Python < 3.0
    #noinspection PyCompatibility, PyUnresolvedReferences
    from urlparse import urlsplit, urlunsplit


# {'commonly used short name': 'long name'}
# we use long names in the API
VCS_NAME_MAP = {
    'git': 'git',
    'hg': 'mercurial',
    'svn': 'subversion',
    'bzr': 'bazaar',
}


# $GIT_DIR/$GIT_WORK_TREE overwrite $CWD as the repository location. And
# because `pip.vcs.git` relies on Git using $CWD, we need to unset those.
# (Pip should use --work-tree=<dir> https://github.com/pypa/pip/issues/1130)
# $GIT_DIR is set for example when `opbeat' is invoked from a Git hook.
os.environ.pop('GIT_DIR', None)
os.environ.pop('GIT_WORK_TREE', None)


def find_vcs_root(path):
    """Walk up the hierarchy and return the first VCS root found."""
    while path and path != '/':
        if is_vcs_root(path):
            return path
        path = os.path.split(path)[0]


def is_vcs_root(path):
    return vcs.get_backend_name(path) is not None


def get_branch(backend, path):
    """
    Return a branch name.

    :type backend: pip.vcs.VersionControl

    """
    if backend.name == 'git':
        output = subprocess.check_output([backend.cmd, 'branch'], cwd=path)
        output = output.decode()
        for branch in output.splitlines():
            if branch.startswith('* '):
                return branch[2:]
    elif backend.name == 'hg':
        output = subprocess.check_output([backend.cmd, 'branch'], cwd=path)
        return output.decode().strip()
    elif backend.name == 'svn':
        output = subprocess.check_output([backend.cmd, 'info'], cwd=path)
        output = output.decode()
        for line in output.splitlines():
            if line.startswith('URL: '):
                return line.split('/')[-1]


class VCS(object):

    def __init__(self, rev, vcs_type=None, branch=None, remote_url=None):

        types = list(VCS_NAME_MAP.values())

        if vcs_type is not None and vcs_type not in types:
            raise InvalidArgumentError(
                'invalid VCS type %r, it has to be one of %s' % (
                    vcs_type,
                    ', '.join(types),
                )
            )
        self.vcs_type = vcs_type
        self.rev = rev
        self.branch = branch
        self.remote_url = (
            expand_ssh_host_alias(remote_url)
            if remote_url else None
        )

    def __repr__(self):
        return (
            '{cls}(rev={rev!r}, vcs_type={vcs_type!r},'
            ' branch={branch!r}, remote_url={remote_url!r})'
            .format(
                cls=type(self).__name__,
                **self.__dict__
            )
        )

    @classmethod
    def from_path(cls, path):
        backend_class = vcs.get_backend_from_location(path)
        if backend_class:
            backend = backend_class()
            return VCS(
                vcs_type=VCS_NAME_MAP[backend.name],
                rev=backend.get_revision(path),
                remote_url=backend.get_url(path),
                branch=get_branch(backend, path),
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
