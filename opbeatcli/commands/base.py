from opbeatcli.client import OpbeatClient
from opbeatcli.log import logger


class CommandBase(object):

    description = None

    def __init__(self, parser, args):
        """
        :type parser: argparse.ArgumentParser
        :type args: argparse.Namespace
        :type logger: logging.Logger

        """
        self.parser = parser
        self.args = args

    def run(self):
        """Do the actual work."""

    @property
    def client(self):
        """Return a client configured based on global args."""
        if not hasattr(self, '_client'):
            self._client = OpbeatClient(
                organization_id=self.args.organization_id,
                app_id=self.args.app_id,
                server=self.args.server,
                secret_token=self.args.secret_token,
                dry_run=self.args.dry_run,
                timeout=self.args.timeout,
            )
        return self._client

    @classmethod
    def add_command_args(cls, subparser):
        """
        Initiate ``parser`` with args specific to this command.

        :param subparser: sub-parser for this command
        :type subparser: argparse.ArgumentParser

        """
