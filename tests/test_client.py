from opbeatcli.client import OpbeatClient
from opbeatcli.exceptions import ClientConnectionError, ClientHTTPError
from opbeatcli import settings

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class ClientTest(unittest.TestCase):

    def test_client_timeout(self):
        client = OpbeatClient(secret_token='TOKEN',
                              organization_id='ORG_ID',
                              app_id='APP_ID',
                              timeout=0)
        with self.assertRaises(ClientConnectionError) as cm:
            client.post('/', {})

        self.assertIn('timeout', str(cm.exception))

    def test_http_404_error(self):
        client = OpbeatClient(secret_token='TOKEN',
                              organization_id='ORG_ID',
                              app_id='APP_ID')
        with self.assertRaises(ClientConnectionError) as cm:
            client.post(settings.DEPLOYMENT_API_URI, {})
        self.assertEqual(cm.exception.args[0], 404)

    def test_client_connection_error(self):
        client = OpbeatClient(secret_token='TOKEN',
                              organization_id='ORG_ID',
                              app_id='APP_ID',
                              server='http://no-resolve.localhost')

        with self.assertRaises(ClientConnectionError):
            client.post('/', {})
