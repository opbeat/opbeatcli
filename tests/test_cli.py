import os

from opbeatcli.cli import ENV
from opbeatcli.core import get_command, main, EXIT_SUCCESS


try:
    import unittest2 as unittest
except ImportError:
    import unittest


class CommonCommonCLIOptionsTest(unittest.TestCase):

    def test_opbeat_cli_no_arguments(self):
        main(args=[])

    def test_opbeat_cli_help(self):
        with self.assertRaises(SystemExit) as cm:
            main(args=['--help'])
        self.assertEqual(cm.exception.code, EXIT_SUCCESS)

    def test_opbeat_cli_version(self):
        with self.assertRaises(SystemExit) as cm:
            main(args=['--version'])
        self.assertEqual(cm.exception.code, EXIT_SUCCESS)

    def test_common_options_environment_variables(self):
        var_names = [
            ENV.APP_ID,
            ENV.ORGANIZATION_ID,
            ENV.SERVER,
            ENV.TOKEN,
        ]

        for name in var_names:
            os.environ[name] = name

        try:
            args = get_command(['deployment']).args
            self.assertEqual(args.app_id, ENV.APP_ID)
            self.assertEqual(
                args.organization_id, ENV.ORGANIZATION_ID)
            self.assertEqual(args.secret_token, ENV.TOKEN)
            self.assertEqual(args.server, ENV.SERVER)

        finally:
            for name in var_names:
                del os.environ[name]
