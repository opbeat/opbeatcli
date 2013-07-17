import unittest
import logging

from opbeatcli.runner import build_client


logger = logging.getLogger('opbeatcli.tests')


SECRET_TOKEN = 'my-access-token'
SERVER = 'http://localhost:8000'
ORGANIZATION_ID = 'organisation-id'
APP_ID = 'app-id'
TIMEOUT = 1.0


class TestBuildClient(unittest.TestCase):

    def test_build_client_basic(self):

        client = build_client(
            organization_id=ORGANIZATION_ID,
            app_id=APP_ID,
            secret_token=SECRET_TOKEN,
            server=SERVER,
            logger=logger,
            dry_run=False
        )

        self.assertEqual(client.logger, logger)
        self.assertEqual(client.organization_id, ORGANIZATION_ID)
        self.assertEqual(client.app_id, APP_ID)
        self.assertEqual(client.secret_token, SECRET_TOKEN)
        self.assertEqual(client.server, SERVER)
        self.assertEqual(client.dry_run, False)
