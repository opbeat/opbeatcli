class OpbeatClientConnectionError(Exception):
    """
    A problem talking to the server, such as timeout or general
    connection error.

    """


class OpbeatClientHTTPError(OpbeatClientConnectionError):
    """Raised when response status >= 400."""
