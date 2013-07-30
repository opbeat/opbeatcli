import os
from opbeatcli.exceptions import InvalidArgumentError
from opbeatcli.deployment.packages import Component
from opbeatcli.deployment.vcs import expand_ssh_host_alias
from opbeatcli import cli
from opbeatcli.commands.deployment import (
    KeyValue, RepoSpecValidator,
    args_to_repo_spec, args_to_local_repo_spec,
    DeploymentCommand
)

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestRepoSpecArgParsingAndValidation(unittest.TestCase):

    def test_syntactically_invalid_key_value_pairs(self):
        invalid = [
            '',
            ':',
            'key:',
            ':value',
            'foo',
        ]
        for arg in invalid:
            with self.assertRaises(InvalidArgumentError):
                KeyValue.from_string(arg)

    def test_repo_spec_validation(self):
        validate = RepoSpecValidator(key1=True, key2=True, key3=False)
        invalid = [
            'key1:foo key1:foo',  # duplicate
            'key1:foo',           # missing
            'undefined:foo',      # unknown
        ]
        for args in invalid:
            pairs = map(KeyValue.from_string, args.split())
            with self.assertRaises(InvalidArgumentError):
                validate(pairs)


class BaseDeploymentTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.PATH = os.path.dirname(__file__)
        cls.DIR_NAME = os.path.basename(cls.PATH)

        cls.PARENT_PATH = os.path.dirname(cls.PATH)
        cls.PARENT_DIR_NAME = os.path.basename(cls.PARENT_PATH)

        os.chdir(cls.PATH)


class BaseComponentTestCase(BaseDeploymentTestCase):

    get_component = None

    def assert_args_to_component(self, cli_args_dict, expected_attributes):
        """
        Check that repo CLI args get properly parsed and the component
        created has all ``attributes``.

        """
        component = self.get_component(cli_args_dict)
        vcs_info = expected_attributes.get('vcs_info', None)

        if vcs_info:
            self.assertIsNotNone(component.vcs_info)
            self.assertDictContainsSubset(
                vcs_info,
                component.vcs_info.__dict__
            )
            del expected_attributes['vcs_info']

        self.assertDictContainsSubset(
            expected_attributes,
            component.__dict__
        )


class TestDeploymentCommandLineArgs(BaseDeploymentTestCase):

    def get_command(self, deployment_args_line=''):
        cmdline = '-o org -a app -t token deployment ' + deployment_args_line
        args = cli.parser.parse_args(cmdline.split())
        self.assertEqual(args.command_class, DeploymentCommand)
        return DeploymentCommand(parser=cli.parser, args=args)

    def test_deployment_no_repos_specified(self):
        """The current directory should be added as a local repo."""
        command = self.get_command()
        repo_specs, local_repo_specs = command.get_repo_specs()
        self.assertFalse(repo_specs)
        self.assertEqual(len(local_repo_specs), 1)
        self.assertDictEqual(
            local_repo_specs[0],
            {
                'path': self.PATH,
                'version': None,
                'name': None
            }
        )

    def test_deployment_legacy_directory(self):
        command = self.get_command('-d .')
        repo_specs, local_repo_specs = command.get_repo_specs()
        self.assertFalse(repo_specs)
        self.assertEqual(len(local_repo_specs), 1)
        self.assertDictEqual(
            local_repo_specs[0],
            {
                'path': '.',
                'version': None,
                'name': None
            }
        )

    def test_deployment_legacy_module(self):
        command = self.get_command('-m my-repo-name')
        repo_specs, local_repo_specs = command.get_repo_specs()
        self.assertFalse(repo_specs)
        self.assertEqual(len(local_repo_specs), 1)
        self.assertDictEqual(
            local_repo_specs[0],
            {
                'path': self.PATH,
                'version': None,
                'name': 'my-repo-name'
            }
        )

    def test_deployment_legacy_directory_and_module(self):
        command = self.get_command('-m my-repo-name -d .')
        repo_specs, local_repo_specs = command.get_repo_specs()
        self.assertFalse(repo_specs)
        self.assertEqual(len(local_repo_specs), 1)
        self.assertDictEqual(
            local_repo_specs[0],
            {
                'path': '.',
                'version': None,
                'name': 'my-repo-name'
            }
        )


class TestComponentFromRepoSpec(BaseComponentTestCase):

    def get_component(self, cli_args_dict):
        """
        :param cli_args_dict: key:value arguments to --repo as a ``dict``
        :return: a ``Component``

        """
        spec = args_to_repo_spec(cli_args_dict.items())
        component = Component.from_repo_spec(spec)
        return component

    def test_component_name_version_vcs_info(self):
        self.assert_args_to_component(
            {
                'name': 'test',
                'version': '1.0',
                'vcs': 'git',
                'rev': 'xxx',
                'branch': 'master',
                'remote_url': 'git@github.com:opbeat/opbeatcli.git',
            },
            {
                'name': 'test',
                'version': '1.0',
                'vcs_info': {
                    'vcs_type': 'git',
                    'rev': 'xxx',
                    'branch': 'master',
                    'remote_url': 'git@github.com:opbeat/opbeatcli.git',
                }
            }
        )

    def test_component_name_version_no_rev(self):
        self.assert_args_to_component(
            {
                'name': 'test',
                'version': '1.0',
            },
            {
                'name': 'test',
                'version': '1.0',
            }
        )

    def test_component_rev_no_version(self):
        self.assert_args_to_component(
            {
                'name': 'test',
                'vcs': 'git',
                'rev': 'xxx',
                'branch': 'master',
                'remote_url': 'git@github.com:opbeat/opbeatcli.git',
            },
            {
                'name': 'test',
                'vcs_info': {
                    'vcs_type': 'git',
                    'rev': 'xxx',
                    'branch': 'master',
                    'remote_url': 'git@github.com:opbeat/opbeatcli.git',
                }
            }
        )

    def test_component_no_version_no_rev(self):
        with self.assertRaises(InvalidArgumentError):
            self.get_component({
                'name': 'test',
            })


class TestComponentFromLocalRepoSpec(BaseComponentTestCase):

    def get_component(self, cli_args_dict):
        """
        :param cli_args_dict: key:value arguments to --local-repo as a ``dict``
        :return: a ``Component``

        """
        spec = args_to_local_repo_spec(cli_args_dict.items())
        component = Component.from_local_repo_spec(spec)
        return component

    def test_local_component_path_does_not_exist(self):
        with self.assertRaises(InvalidArgumentError):
            self.get_component({
                'path': os.path.join(self.PATH, 'xxx')
            })

    def test_local_component_path_exists_but_no_cvs(self):
        with self.assertRaises(InvalidArgumentError):
            self.get_component({
                'path': '/',
                'name': 'test'
            })

    def test_component_from_local_spec_with_relative_path(self):
        self.assert_args_to_component(
            {
                'path': '.'
            },
            {
                'name': self.DIR_NAME,
                'vcs_info': {'vcs_type': 'git'}
            }
        )

    def test_component_from_local_spec_with_relative_path2(self):
        self.assert_args_to_component(
            {
                'path': '..'
            },
            {
                'name': self.PARENT_DIR_NAME,
                'vcs_info': {'vcs_type': 'git'}
            }
        )

    def test_component_from_local_spec_with_absolute_path(self):
        self.assert_args_to_component(
            {
                'path': self.PATH
            },
            {
                'name': self.DIR_NAME,
                'vcs_info': {'vcs_type': 'git'}
            }
        )


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