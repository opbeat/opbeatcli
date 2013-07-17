import unittest
import os
from opbeatcli.credentials import get_default_filename, get_config, save_config, load_credentials, save_credentials
from datetime import datetime, timedelta

config_file = "test_config.ini"

class TestCredentials(unittest.TestCase):
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

    def test_get_default_filename(self):
        self.assertNotEqual(None, get_default_filename())

    def test_get_config_fail(self):
        self.assertRaises(IOError, get_config, config_file)

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

    def test_save_access_token(self):
        access_token = "ac_token"
        refresh_token = "re_token"
        expires = datetime.now() + timedelta(days=1)

        save_credentials(access_token, refresh_token, expires, config_file)

    def test_save_and_load_access_token(self):
        access_token = "ac_token"
        expires = datetime.now().replace(microsecond=0) + timedelta(days=1)
        refresh_token = "re_token"

        save_credentials(access_token, refresh_token,expires, config_file)

        credentials = load_credentials(config_file)

        self.assertEqual(credentials['access_token'], access_token)
        self.assertEqual(credentials['refresh_token'], refresh_token)
        self.assertEqual(credentials['expires'], expires)
