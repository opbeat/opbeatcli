import subprocess

try:
    from subprocess import check_output
except ImportError:  # Python 2.6
    def check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        Back-ported from Python 2.7 as it's implemented as pure python on
        stdlib.

        >>> check_output(['/usr/bin/python', '--version'])
        Python 2.6.2
        """
        process = subprocess.Popen(
            stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output

try:
    #noinspection PyCompatibility
    from urllib.request import Request, urlopen, URLError, HTTPError
    #noinspection PyCompatibility
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python < 3.0
    #noinspection PyCompatibility,PyUnresolvedReferences
    from urllib2 import Request, urlopen, URLError, HTTPError
    #noinspection PyCompatibility,PyUnresolvedReferences
    from BaseHTTPServer import BaseHTTPRequestHandler


try:
    #noinspection PyCompatibility
    from urllib.parse import urlsplit, urlunsplit
except ImportError:  # Python < 3.0
    #noinspection PyCompatibility,PyUnresolvedReferences
    from urlparse import urlsplit, urlunsplit
