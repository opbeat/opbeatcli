import unittest
from opbeatcli.client import Client
from opbeatcli.credentials import get_config
import logging

logger = logging.getLogger('opbeatcli.tests')

SECRET_TOKEN = 'my-access-token'
SERVER = 'http://localhost:8000'

ORGANIZATION_ID = 'organiation-id'
APP_ID = 'app-id'
TIMEOUT = 1.0

config_file = "opbeatcli_test.config"

class TestClient(unittest.TestCase):
	def setUp(self):
		try:
			os.remove(config_file)
		except:
			pass

	def tearDown(self):
		try:
			os.remove(config_file)
		except:
			pass

	def test_setup_client_basic(self):
		client = Client(logger, ORGANIZATION_ID, APP_ID, SECRET_TOKEN, SERVER)
		self.assertEqual(client.logger, logger)
		self.assertEqual(client.secret_token, SECRET_TOKEN)
		self.assertEqual(client.server, SERVER)

		self.assertEqual(client.dry_run, False)

	def test_setup_client_with_orgid_and_timeout(self):
		client = Client(logger, ORGANIZATION_ID, APP_ID, SECRET_TOKEN, SERVER, TIMEOUT)

		self.assertEqual(client.logger, logger)
		self.assertEqual(client.secret_token, SECRET_TOKEN)
		self.assertEqual(client.server, SERVER)

		self.assertEqual(client.organization_id, ORGANIZATION_ID)
		self.assertEqual(client.app_id, APP_ID)
		self.assertEqual(client.timeout, TIMEOUT)

		self.assertEqual(client.dry_run, False)

	def test_setup_client_with_orgid_and_timeout_and_dryrun(self):
		client = Client(logger, ORGANIZATION_ID, APP_ID, SECRET_TOKEN, SERVER,
						1.0, True)

		self.assertEqual(client.logger, logger)
		self.assertEqual(client.secret_token, SECRET_TOKEN)
		self.assertEqual(client.server, SERVER)

		self.assertEqual(client.organization_id, ORGANIZATION_ID)
		self.assertEqual(client.app_id, APP_ID)
		self.assertEqual(client.timeout, TIMEOUT)

		self.assertEqual(client.dry_run, True)

	def test_get_config_basic(self):
		value = "Avalue"
		f = open(config_file,'w')
		f.write(
"""
[justtesting]
akey = %s
""" % value)
		f.close()

		config = get_config(config_file)

		self.assertEqual(config.get("justtesting", "akey"), value)
