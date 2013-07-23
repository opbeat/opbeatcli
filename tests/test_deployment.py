import os

from opbeatcli.exceptions import InvalidArgumentError
from opbeatcli.deployment.packages import Component
from opbeatcli.deployment.vcs import expand_ssh_host_alias

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestComponentFromSpec(unittest.TestCase):

    def assert_spec_parsed_into(self, spec, attributes):
        component = Component.from_repo_spec(spec)
        self.assertDictContainsSubset(component.__dict__, attributes)

    def test_component_from_spec_with_path_only(self):
        self.assert_spec_parsed_into('/app', {
            'path': '/app',
            'name': 'app',
            'version': None,
        })

    def test_component_from_spec_with_path_name_and_version(self):
        self.assert_spec_parsed_into('/app:my-app@v1.0', {
            'path': '/app',
            'name': 'my-app',
            'version': 'v1.0',
        })

    def test_component_from_spec_with_path_and_version(self):
        self.assert_spec_parsed_into('/app@v1.0', {
            'path': '/app',
            'name': 'app',
            'version': 'v1.0',
        })

    def test_component_from_spec_with_relative_path(self):
        self.assert_spec_parsed_into('..', {
            'path': os.path.abspath('..'),
            'name': os.path.basename(os.path.abspath('..')),
            'version': None,
        })

    def test_component_from_spec_invalid(self):
        invalid_specs = [
            '',
            '/',   # Invalid because we cannot not infer name
            ':aa',
            '/foo:@aa',
            '.:',
            '/www:app@q123@',
        ]
        for spec in invalid_specs:
            with self.assertRaises(InvalidArgumentError):
                Component.from_repo_spec(spec)


class TestSSHAliasExpansion(unittest.TestCase):

    class MockSshConfig(object):

        def lookup(self, host):
            try:
                return {
                    'opbeat_python': {
                        'hostname': 'github.com'
                    }
                }[host]
            except KeyError:
                return {
                    'hostname': host
                }

    def assert_url_after_expansion_equals(self, url, expected):
        actual = expand_ssh_host_alias(url, self.MockSshConfig())
        self.assertEqual(actual, expected)

    def test_pass_through_no_config(self):
        url = 'git@github.com:opbeat/opbeatcli.git'
        self.assert_url_after_expansion_equals(url, url)

    def test_pass_through(self):
        url = 'git@github.com:opbeat/opbeatcli.git'
        self.assert_url_after_expansion_equals(url, url)

    def test_expand_git(self):
        self.assert_url_after_expansion_equals(
            'git@opbeat_python:opbeat/opbeat_python.git',
            'git@github.com:opbeat/opbeat_python.git'
        )

    def test_expand_mercurial(self):
        self.assert_url_after_expansion_equals(
            'ssh://hg@opbeat_python/username/reponame/',
            'ssh://hg@github.com/username/reponame/'
        )

    def test_expand_readonly_url(self):
        self.assert_url_after_expansion_equals(
            'git://opbeat_python/roncohen/django-hstore.git',
            'git://github.com/roncohen/django-hstore.git',
        )

    def test_pass_through_http(self):
        url = 'https://github.com/omab/django-social-auth.git'
        self.assert_url_after_expansion_equals(url, url)
