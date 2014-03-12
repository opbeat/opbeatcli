import os
import shlex
import datetime
import shutil
import tempfile
import subprocess
from operator import attrgetter

from pip.vcs import vcs as pip_vcs
from pip.exceptions import BadCommand

from opbeatcli.deployment.packages.deb import DebDependency
from opbeatcli.deployment.packages.nodejs import NodeDependency
from opbeatcli.deployment.packages.other import OtherDependency
from opbeatcli.deployment.packages.python import PythonDependency
from opbeatcli.deployment.packages.rpm import RPMDependency
from opbeatcli.deployment.packages.ruby import RubyDependency
from opbeatcli.deployment.packages.component import Component
from opbeatcli.deployment.vcs import expand_ssh_host_alias
from opbeatcli.core import get_command, main, EXIT_SUCCESS
from opbeatcli.commands.deployment import KeyValue, PackageSpecValidator
from opbeatcli.exceptions import (InvalidArgumentError,
                                  DependencyParseError,
                                  ExternalCommandNotFoundError)
#noinspection PyUnresolvedReferences
import settings


try:
    import unittest2 as unittest
except ImportError:
    import unittest


# Homebrew-installed VCS tools may be there but not on PATH.
os.environ['PATH'] += ':/usr/local/bin'


def get_vcs_command(vcs_type):
    """Find the command using a Pip VCS backend.

    """
    try:
        return pip_vcs.get_backend(vcs_type)().cmd
    except BadCommand:
        pass


class TestPackageSpecArgParsingAndValidation(unittest.TestCase):
    """Low-level tests for package argument parsing."""

    def test_key_value_pair_parsing(self):
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
        validate = PackageSpecValidator(key1=True, key2=True, key3=False)
        invalid = [
            'key1:foo key1:foo',  # duplicate
            'key1:foo',           # missing
            'undefined:foo',      # unknown
        ]
        for args in invalid:
            pairs = map(KeyValue.from_string, args.split())
            with self.assertRaises(InvalidArgumentError):
                validate(pairs)


class _BaseDeploymentCommandTestCase(unittest.TestCase):

    maxDiff = 9999

    @classmethod
    def setUpClass(cls):
        cls.PATH = os.path.dirname(__file__)
        cls.DIR_NAME = os.path.basename(cls.PATH)
        os.chdir(cls.PATH)

    def get_deployment_command(self, cmdline):
        cmdline = '-t token -o org -a app deployment ' + cmdline
        return get_command(shlex.split(cmdline))

    def assert_package_attributes(self, component, expected_attributes):
        """
        Check that repo CLI args get properly parsed and the component
        created has all ``attributes``.

        """
        vcs = expected_attributes.get('vcs', None)
        if vcs:
            self.assertIsNotNone(component.vcs)
            self.assertDictContainsSubset(vcs,  component.vcs.__dict__)
            del expected_attributes['vcs']

        self.assertDictContainsSubset(
            expected_attributes,
            component.__dict__
        )


class DeploymentCommandTest(_BaseDeploymentCommandTestCase):

    def test_deployment_send_data(self):
        now = datetime.datetime.now().isoformat()
        args = """
        deployment
            --component path:.
            --component path:/dummy/component name:now version:{now}
            --dependency type:other name:now version:{now}

        """.format(now=now)
        exit_status = main(settings.AUTH_ARGS + args.split())
        self.assertEqual(exit_status, EXIT_SUCCESS)

    def test_deployment_help(self):
        # the --help action exits with 0
        with self.assertRaises(SystemExit) as cm:
            main('deployment --help'.split())
        self.assertEqual(cm.exception.code, EXIT_SUCCESS)

    def test_deployment_dry_run(self):
        exit_status = main(
            """
            -o O -a A -t T
            --dry-run
            deployment --component path:.
            """.split()
        )
        self.assertEqual(exit_status, EXIT_SUCCESS)

    def test_deployment_verbose_dry_run(self):
        exit_status = main(
            """
            -o O -a A -t T
            --verbose --dry-run
            deployment --component path:.
            """.split()
        )
        self.assertEqual(exit_status, EXIT_SUCCESS)


class DeploymentVCSComponentsTest(_BaseDeploymentCommandTestCase):

    def test_component_arg_from_local_git_repo(self):
        command = self.get_deployment_command('--component path:.')
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, Component)
        self.assert_package_attributes(package, {
            'path': self.PATH,
            'name': self.DIR_NAME,
            'version': None,
            'vcs': {
                'vcs_type': 'git',
            }
        })
        self.assertIn('opbeat/opbeatcli.git', package.vcs.remote_url)
        self.assertIsNotNone(package.vcs.branch)
        self.assertIsNotNone(package.vcs.rev)

    def test_component_arg_from_local_git_repo_with_no_remote(self):
        git = get_vcs_command('git')
        repo = tempfile.mkdtemp()

        try:
            subprocess.check_call([git, 'init'], cwd=repo)
            with open(os.path.join(repo, "readme.md"), "w") as readme_file:
                readme_file.write("Temp. readme file")

            subprocess.check_call([git, 'add', '.'], cwd=repo)
            subprocess.check_call(
                [git, 'commit', '-m', 'Initial commit'], cwd=repo)

            command = self.get_deployment_command(
                '--component path:{}'.format(repo))
            packages = command.get_packages_from_args()
            self.assertEqual(len(packages), 1)
            package = packages[0]
            self.assertIsInstance(package, Component)
            self.assert_package_attributes(package, {
                'path': repo,
                'name': repo.split("/")[-1],
                'version': None,
                'vcs': {
                    'vcs_type': 'git',
                }
            })
            self.assertEqual(None, package.vcs.remote_url)
            self.assertIsNotNone(package.vcs.branch)
            self.assertIsNotNone(package.vcs.rev)
        finally:
            shutil.rmtree(repo)

    @unittest.skipIf(not get_vcs_command('hg'), 'mercurial not available')
    def test_component_arg_from_local_mercurial_repo(self):

        hg = get_vcs_command('hg')
        repo = tempfile.mkdtemp()
        branch = 'test-branch'

        try:
            subprocess.check_call([hg, 'init'], cwd=repo)
            subprocess.check_call([hg, 'branch', branch], cwd=repo)

            command = self.get_deployment_command(
                '--component path:%r' % str(repo))
            packages = command.get_packages_from_args()
            self.assertEqual(len(packages), 1)
            package = packages[0]
            self.assertIsInstance(package, Component)
            self.assert_package_attributes(package, {
                'path': repo,
                'name': os.path.basename(repo),
                'version': None,
                'vcs': {
                    'vcs_type': 'mercurial',
                    'branch': branch,
                }
            })
            self.assertIsNotNone(package.vcs.branch)

        finally:
            shutil.rmtree(repo)

    @unittest.skipIf(not get_vcs_command('svn'), 'subversion not available')
    def test_component_arg_from_local_subversion_repo(self):

        svn = get_vcs_command('svn')
        repo = tempfile.mkdtemp()
        try:
            subprocess.check_call([
                svn, 'checkout',
                '--non-interactive',
                '--trust-server-cert',
                'https://github.com/opbeat/opbeatcli/trunk',
                repo
            ])
            command = self.get_deployment_command(
                '--component path:%r' % str(repo))
            packages = command.get_packages_from_args()
            self.assertEqual(len(packages), 1)
            package = packages[0]
            self.assertIsInstance(package, Component)
            self.assert_package_attributes(package, {
                'path': repo,
                'name': os.path.basename(repo),
                'version': None,
                'vcs': {
                    'vcs_type': 'subversion',
                    'branch': 'trunk',
                    'remote_url': 'https://github.com/opbeat/opbeatcli/trunk'
                }
            })
            self.assertIsNotNone(package.vcs.rev)

        finally:
            shutil.rmtree(repo)

    @unittest.skipIf(not get_vcs_command('bzr'), 'bazaar not available')
    def test_component_arg_from_local_bazaar_repo(self):

        bzr = get_vcs_command('bzr')
        repo = tempfile.mkdtemp()
        try:
            subprocess.check_call([bzr, 'init', repo])
            command = self.get_deployment_command(
                '--component path:%r' % str(repo))
            packages = command.get_packages_from_args()
            self.assertEqual(len(packages), 1)
            package = packages[0]
            self.assertIsInstance(package, Component)
            self.assert_package_attributes(package, {
                'path': repo,
                'name': os.path.basename(repo),
                'version': None,
                'vcs': {
                    'vcs_type': 'bazaar',
                    'branch': None,
                    'rev': '0'
                }
            })

        finally:
            shutil.rmtree(repo)


class DeploymentCLIPackagesTest(_BaseDeploymentCommandTestCase):
    """Test --component and --dependency parsing."""

    def test_component_from_legacy_directory_arg(self):
        command = self.get_deployment_command('-d .')
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, Component)
        self.assert_package_attributes(package, {
            'path': self.PATH,
            'name': self.DIR_NAME,
            'vcs': {
                'vcs_type': 'git'
            }
        })

    def test_component_from_legacy_directory_and_module_args(self):
        command = self.get_deployment_command('-d . -m NAME')
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, Component)
        self.assert_package_attributes(package, {
            'path': self.PATH,
            'name': 'NAME',
            'vcs': {
                'vcs_type': 'git'
            }
        })

    def test_component_arg_all_attributes(self):
        command = self.get_deployment_command("""
            --component
                path:/PATH
                name:NAME
                version:VERSION
                vcs:git
                rev:REV
                branch:BRANCH
                remote_url:REMOTE
        """)
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, Component)
        self.assert_package_attributes(package, {
            'path': '/PATH',
            'name': 'NAME',
            'version': 'VERSION',
            'vcs': {
                'vcs_type': 'git',
                'branch': 'BRANCH',
                'rev': 'REV',
                'remote_url': 'REMOTE'
            }
        })

    def test_component_arg_name_optional(self):
        command = self.get_deployment_command(
            '--component path:/PATH version:VERSION'
        )
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, Component)
        self.assertEqual(package.name, 'PATH')

    def test_component_arg_version_or_rev_required(self):
        command = self.get_deployment_command('--component path:/PATH')
        with self.assertRaises(InvalidArgumentError):
            command.get_packages_from_args()

    def test_component_arg_path_required(self):
        command = self.get_deployment_command(
            '--component name:NAME version:VERSION'
        )
        with self.assertRaises(InvalidArgumentError):
            command.get_packages_from_args()

    def test_dependency_arg_all_attributes(self):
        command = self.get_deployment_command("""
            --dependency
                type:other
                name:NAME
                version:VERSION
                vcs:git
                rev:REV
                branch:BRANCH
                remote_url:REMOTE
        """)
        packages = command.get_packages_from_args()
        self.assertEqual(len(packages), 1)
        package = packages[0]
        self.assertIsInstance(package, OtherDependency)
        self.assert_package_attributes(package, {
            'name': 'NAME',
            'version': 'VERSION',
            'vcs': {
                'vcs_type': 'git',
                'branch': 'BRANCH',
                'rev': 'REV',
                'remote_url': 'REMOTE'
            }
        })

    def test_dependency_arg_version_or_rev_required(self):
        command = self.get_deployment_command(
            '--dependency type:other name:NAME'
        )
        with self.assertRaises(InvalidArgumentError):
            command.get_packages_from_args()

    def test_dependency_arg_type_required(self):
        command = self.get_deployment_command(
            '--dependency name:NAME version:VERSION'
        )
        with self.assertRaises(InvalidArgumentError):
            command.get_packages_from_args()

    def test_dependency_arg_name_required(self):
        command = self.get_deployment_command(
            '--dependency type:other version:VERSION'
        )
        with self.assertRaises(InvalidArgumentError):
            command.get_packages_from_args()


class TestDependencyCollection(_BaseDeploymentCommandTestCase):
    """Test automatic dependency collection with valid and invalid output."""

    def test_collect_dependencies_duplicate_type(self):
        with self.assertRaises(InvalidArgumentError):
            list(
                self.get_deployment_command(
                    '--collect-dependencies python python'
                ).get_all_packages()
            )

    def test_auto_collect_dependencies(self):
        self.assertGreater(len(list(
            self.get_deployment_command('')
                .get_all_packages()
        )), 1)

    def test_auto_collect_dependencies_overwrite_type(self):
        packages = list(
            self.get_deployment_command("""
                --collect-dependencies
                    python:'echo NAME==VERSION'
            """).get_all_packages()
        )
        python_deps = [
            package for package in packages
            if isinstance(package, PythonDependency)
        ]

        self.assertEqual(len(python_deps), 1)
        self.assert_package_attributes(python_deps[0], {
            'name': 'NAME',
            'version': 'VERSION',
        })

    def test_auto_collect_dependencies_extend_type(self):

        python_dep_count = sum(
            isinstance(package, PythonDependency)
            for package in self.get_deployment_command('').get_all_packages()
        )
        python_dep_count_extended = sum(
            isinstance(package, PythonDependency)
            for package in self.get_deployment_command("""
                --collect-dependencies
                    python
                    python:'echo NAME==VERSION'
            """).get_all_packages()
        )

        self.assertEqual(python_dep_count_extended - python_dep_count, 1)

    def test_no_auto_collect_dependencies(self):
        packages = list(
            self.get_deployment_command('--no-auto-collect-dependencies')
                .get_all_packages()
        )
        self.assertEqual(len(packages), 0)

    def test_collect_dependencies_command_for_explicit_type_not_found(self):
        """
        When we are explicit about a type[:command] and the command does not
        exists, then it's an error. (As opposed to calling
        --collect-dependencies with no args where we ignore missing default
        commands)

        """
        with self.assertRaises(ExternalCommandNotFoundError):
            list(self.get_deployment_command(
                '--collect-dependencies python:/NOT/A/CMD').get_all_packages())

    def test_collect_dependencies_default_and_custom_commands(self):
        list(
            self.get_deployment_command(
                '--collect-dependencies python python:"echo PACKAGE==VERSION"'
            ).get_all_packages()
        )

    def test_collect_python(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies python:"cat fixtures/pip_freeze.txt"
        """)
        dependencies = list(command.collect_dependencies())
        self.assertEqual(len(dependencies), 7)
        self.assertTrue(all(isinstance(dep, PythonDependency)
                            for dep in dependencies))
        expected = [
            {
                'name': 'MyPackage',
                'version': '3.0'
            },
            {
                'name': 'opbeatcli',
                'version': 'dev',
                'vcs': {
                    'vcs_type': 'git',
                    'remote_url': 'git@github.com:opbeat/opbeatcli.git',
                    'rev': 'a27946a613b84b1b0a8f029b8ec1f08d87565db9'

                }
            },
            {
                'name': 'ipython',
                'version': 'dev',
                'vcs': {
                    'vcs_type': 'git',
                    'remote_url': 'https://github.com/ipython/ipython.git',
                    'rev': 'dbf7918fdeb54b3fb2946c4492d6fce867356404'

                }
            },
            {
                'name': 'project',
                'version': 'dev',
                'vcs': {
                    'vcs_type': 'git',
                    'remote_url': 'git://git.project.org/project.git',
                    'rev': 'asdasdasd',

                }
            },
            {
                'name': 'project-project',
                'version': 'dev',
                'vcs': {
                    'vcs_type': 'mercurial',
                    'remote_url': 'http://hg.project.org/project/',
                    'rev': 'da39a3ee5e6b',

                }
            },
            {
                'name': 'project',
                'version': 'dev',
                'vcs': {
                    'vcs_type': 'bazaar',
                    'remote_url': 'https://bzr.project.org/project/trunk/',
                    'rev': '2019',

                }
            },
            {
                'name': 'project',
                'version': None,
                'vcs': {
                    'vcs_type': 'subversion',
                    'remote_url': 'http://svn.project.org/svn/project/trunk',
                    'rev': '2019',

                }
            },
        ]
        for dependency, attrs in zip(dependencies, expected):
            self.assert_package_attributes(dependency, attrs)

    def test_collect_python_parse_error(self):
        command = self.get_deployment_command(
            '--collect-dependencies python:"echo invalid-requirement="'
        )
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())

    def test_collect_python_parse_error_editable(self):
        command = self.get_deployment_command(
            '--collect-dependencies python:"echo \'-e foo\'"'
        )
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())

    def test_collect_nodejs(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies nodejs:"cat fixtures/npm_list.json"
        """)
        dependencies = list(command.collect_dependencies())

        self.assertEqual(len(dependencies), 5)

        self.assertTrue(all(isinstance(dep, NodeDependency)
                            for dep in dependencies))
        dependencies = sorted(dependencies, key=attrgetter('name'))

        expected = [
            {'name': 'brunch', 'version': '1.7.0'},
            {'name': 'coffee-script', 'version': '1.6.2'},
            {'name': 'grunt-cli', 'version': '0.1.8'},
            {'name': 'rrule', 'version': '1.0.1'},
            {'name': 'yo', 'version': '1.0.0-beta.5'},
        ]

        for dependency, attrs in zip(dependencies, expected):
            self.assert_package_attributes(dependency, attrs)

    def test_collect_nodejs_parse_error(self):
        command = self.get_deployment_command(
            '--collect-dependencies nodejs:"echo invalid-json"'
        )
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())

    def test_collect_ruby(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies
                ruby:'cat fixtures/gem_list.txt'
        """)
        dependencies = list(command.collect_dependencies())

        self.assertEqual(len(dependencies), 36)
        self.assertTrue(all(isinstance(dep, RubyDependency)
                            for dep in dependencies))

        expected = [
            {'name': 'actionmailer', 'version': '3.2.12'},
            {'name': 'actionmailer', 'version': '3.0.9'},
            {'name': 'actionmailer', 'version': '3.0.5'},
            {'name': 'actionpack', 'version': '3.2.12'},
        ]

        for dependency, attrs in zip(dependencies, expected):
            self.assert_package_attributes(dependency, attrs)

    def test_collect_ruby_parse_error(self):
        command = self.get_deployment_command(
            '--collect-dependencies ruby:"echo invalid-gem-spec-no-versions"'
        )
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())

    def test_collect_deb(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies
                deb:'cat fixtures/dpkg_query.txt'
        """)
        dependencies = list(command.collect_dependencies())

        self.assertEqual(len(dependencies), 25)

        self.assertTrue(all(isinstance(dep, DebDependency)
                            for dep in dependencies))
        expected = [
            {'name': 'accountsservice', 'version': '0.6.15-2ubuntu9.6'},
            {'name': 'acpid', 'version': '1:2.0.10-1ubuntu3'},
        ]

        for dependency, attrs in zip(dependencies, expected):
            self.assert_package_attributes(dependency, attrs)

    def test_collect_deb_parse_error(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies
                deb:'echo invalid-deb-package-no-version'
        """)
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())

    def test_collect_rpm(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies
                rpm:'cat fixtures/rpm_query.txt'
        """)
        dependencies = list(command.collect_dependencies())

        self.assertEqual(len(dependencies), 25)
        self.assertTrue(all(isinstance(dep, RPMDependency)
                            for dep in dependencies))

        expected = [
            {'name': 'libaio', 'version': '0.3.1095.fc17'},
            {'name': 'python3', 'version': '3.2.37.fc17'},
        ]

        for dependency, attrs in zip(dependencies, expected):
            self.assert_package_attributes(dependency, attrs)

    def test_collect_rpm_parse_error(self):
        command = self.get_deployment_command("""
            --no-auto-collect-dependencies
            --collect-dependencies
                rpm:'echo invalid-rpm-package-no-version'
        """)
        with self.assertRaises(DependencyParseError):
            list(command.collect_dependencies())


class DeploymentAPIVersion1SerializationTest(_BaseDeploymentCommandTestCase):
    """Test serialization as per the Opbeat API version 1 docs."""

    def test_deployment_v1_serialization(self):
        command = self.get_deployment_command("""
            --hostname HOSTNAME

            --component path:/PATH name:COMPONENT1 version:1.0
            --component path:/PATH name:COMPONENT2 version:VERSION vcs:git
                        branch:BRANCH rev:REV remote_url:REMOTE_URL

            --no-auto-collect-dependencies

            --dependency type:other name:DEPENDENCY1 version:VERSION
            --dependency name:DEPENDENCY2 type:other version:VERSION vcs:git
                        branch:BRANCH rev:REV remote_url:REMOTE_URL

        """)

        data = command.get_data()
        self.assertDictEqual(data, {
            'machines': [
                {
                    'hostname': 'HOSTNAME'
                }
            ],
            'releases': [
                {
                    'path': '/PATH',
                    'version': '1.0',
                    'module': {
                        'type': 'repository',
                        'name': 'COMPONENT1'
                    }
                },
                {
                    'path': '/PATH',
                    'version': 'VERSION',
                    'vcs': {
                        'type': 'git',
                        'branch': 'BRANCH',
                        'repository': 'REMOTE_URL',
                        'revision': 'REV'
                    },
                    'module': {
                        'type': 'repository',
                        'name': 'COMPONENT2',
                    }
                },
                {
                    'version': 'VERSION',
                    'module': {
                        'type': 'other',
                        'name': 'DEPENDENCY1',
                    }
                },
                {
                    'version': 'VERSION',
                    'vcs': {
                        'type': 'git',
                        'branch': 'BRANCH',
                        'repository': 'REMOTE_URL',
                        'revision': 'REV'},
                    'module': {
                        'name': 'DEPENDENCY2',
                        'type': 'other',
                    }
                }
            ]
        })


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


if __name__ == '__main__':
    unittest.main()
