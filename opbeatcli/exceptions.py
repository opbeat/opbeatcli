#noinspection PyCompatibility
import argparse


class OpbeatError(Exception):
    """
    Our base exception. It's not shown to the user, because it's assumed
    an error message has been logged.

    """


class InvalidArgumentError(OpbeatError, argparse.ArgumentTypeError):
    """Invalid command line argument"""


class ClientConnectionError(OpbeatError):
    """
    A problem talking to the server, such as timeout or general
    connection error.

    """


class ClientHTTPError(ClientConnectionError):
    """Raised when response status >= 400."""


class ExternalCommandError(OpbeatError):
    """Error running an external command."""


class ExternalCommandNotFoundError(ExternalCommandError):
    """Dependency collector command not found."""


class DependencyParseError(ExternalCommandError):
    """Unparseable output."""
