from opbeatcli.client import OpbeatClient
from opbeatcli.log import logger


class CommandBase(object):

    DESCRIPTION = ''
    EPILOG = ''

    def __init__(self, parser, args):
        """
        :type parser: argparse.ArgumentParser
        :type args: argparse.Namespace

        """
        self.parser = parser
        self.args = args
        self.logger = logger.getChild(
            type(self).__name__.replace('Command', '').lower())

    def run(self):
        """Do the actual work."""

    @property
    def client(self):
        """Return a client configured based on global args."""
        if not hasattr(self, '_client'):
            #noinspection PyAttributeOutsideInit
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

        No-op by default.

        :param subparser: sub-parser for this command
        :type subparser: argparse.ArgumentParser

        """
