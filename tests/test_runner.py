import unittest
from opbeatcli.client import Client
from opbeatcli.credentials import get_config
from opbeatcli.runner import build_client
import logging

logger = logging.getLogger('opbeatcli.tests')

SECRET_TOKEN = 'my-access-token'
SERVER = 'http://localhost:8000'

ORGANIZATION_ID = 'organiation-id'
APP_ID = 'app-id'
TIMEOUT = 1.0


class TestBuildClient(unittest.TestCase):
    def test_build_client_basic(self):
        client = build_client(ORGANIZATION_ID, APP_ID, SECRET_TOKEN, SERVER, logger,
                dry_run=False)

        self.assertEqual(client.logger, logger)
        self.assertEqual(client.organization_id, ORGANIZATION_ID)
        self.assertEqual(client.app_id, APP_ID)
        self.assertEqual(client.secret_token, SECRET_TOKEN)
        self.assertEqual(client.server, SERVER)

        self.assertEqual(client.dry_run, False)
