import unittest
import mock
import os
from datetime import datetime, timedelta

from opbeat.commands.deployment import annotate_url_with_ssh_config_info

class MockSshConfig(object):
	def lookup(self, host):
		try:
			return {'opbeat_python':{'hostname':'github.com'}}[host]
		except:
			return {'hostname':host}

class TestDeployment(unittest.TestCase):
	def setUp(self):
		pass


	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_pass_through_no_config(self, get_ssh_config):
		get_ssh_config.return_value = None
		pass_through_url = "git@github.com:opbeat/opbeatcli.git"

		actual_url = annotate_url_with_ssh_config_info(pass_through_url)

		self.assertEqual(pass_through_url,actual_url)

	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_pass_through(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()
		pass_through_url = "git@github.com:opbeat/opbeatcli.git"

		actual_url = annotate_url_with_ssh_config_info(pass_through_url)

		self.assertEqual(pass_through_url,actual_url)

	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_annotate(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='git@opbeat_python:opbeat/opbeat_python.git'
		actual_url = annotate_url_with_ssh_config_info(url)

		self.assertEqual('git@github.com:opbeat/opbeat_python.git',actual_url)

	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_annotate_mercurial(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url = 'ssh://hg@opbeat_python/username/reponame/'
		actual_url = annotate_url_with_ssh_config_info(url)

		self.assertEqual('ssh://hg@github.com/username/reponame/',actual_url)
	
	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_annotate_readonly_url(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='git://opbeat_python/roncohen/django-hstore.git'
		actual_url = annotate_url_with_ssh_config_info(url)

		self.assertEqual('git://github.com/roncohen/django-hstore.git',actual_url)
	
	@mock.patch('opbeat.commands.deployment.get_ssh_config')
	def test_pass_through_http(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='https://github.com/omab/django-social-auth.git'
		actual_url = annotate_url_with_ssh_config_info(url)

		self.assertEqual(url,actual_url)
