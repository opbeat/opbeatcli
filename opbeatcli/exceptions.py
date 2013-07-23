class OpbeatError(Exception):
    """
    Our base exception. It's not shown to the user, because it's assumed
    an error message has been logged.

    """


class InvalidArgumentError(OpbeatError):
    """Invalid command line argument"""


class ClientConnectionError(OpbeatError):
    """
    A problem talking to the server, such as timeout or general
    connection error.

    """


class ClientHTTPError(ClientConnectionError):
    """Raised when response status >= 400."""
