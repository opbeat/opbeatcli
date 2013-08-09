"""
Opbeat log API client.

"""
import json
import logging

from opbeatcli import __version__
from opbeatcli.log import logger
from opbeatcli import settings
from opbeatcli.exceptions import ClientConnectionError, ClientHTTPError


try:
    #noinspection PyCompatibility
    from urllib.request import Request, urlopen, URLError, HTTPError
    #noinspection PyCompatibility
    from http.server import BaseHTTPRequestHandler

except ImportError:
    #noinspection PyCompatibility,PyUnresolvedReferences
    from urllib2 import Request, urlopen, URLError, HTTPError
    #noinspection PyCompatibility,PyUnresolvedReferences
    from BaseHTTPServer import BaseHTTPRequestHandler


HTTP_RESPONSE_CODES = BaseHTTPRequestHandler.responses


class OpbeatClient(object):
    """
    The Opbeat client, which handles communication with the
    Opbeat servers.

    """
    def __init__(self, secret_token, organization_id, app_id,
                 server=settings.SERVER, timeout=settings.TIMEOUT,
                 dry_run=False):

        self.server = server
        self.secret_token = secret_token
        self.organization_id = organization_id
        self.app_id = app_id

        self.timeout = timeout
        self.dry_run = dry_run

        self.logger = logger.getChild('client')

        self.logger.info('Opbeat client configuration:')
        for k in ['server', 'organization_id', 'app_id']:
            self.logger.info('  %16s: %r' % (k, str(getattr(self, k))))

    def log_request(self, uri, headers, payload):
        """
        :type request: Request
        """
        self.logger.debug('> Server: %s', self.server)
        self.logger.debug('> HTTP/1.1 POST %s', uri)
        for header, value in headers.items():
            self.logger.debug('> %s: %s', header, value)
        self.logger.debug('> %s', payload)

    def log_response(self, response, level=logging.DEBUG):
        """
        :type response: HTTPResponse
        """
        self.logger.log(level, '< HTTP %d %s',
                        response.code,
                        HTTP_RESPONSE_CODES[response.code][0])

        body = response.read()

        if body:
            self.logger.log(level, '< %s', body)

    def post(self, uri, data):
        """
        HTTP POST ``data`` as JSON to collection identified by ``uri``.

        :param uri:
            The collection URI. It can be in the form of a URI template
            with the variables {organization_id} and {app_id}, e.g.:

                /api/{organization_id}/apps/{app_id}/deployments/

        :param data: the data to be send
        :type data: dict

        """
        uri = uri.format(
            organization_id=self.organization_id,
            app_id=self.app_id
        )
        url = self.server + uri

        headers = {
            'User-Agent': 'opbeatcli/%s' % __version__,
            'Authorization': 'Bearer %s' % self.secret_token,
            'Content-Type': 'application/json',
        }
        payload = json.dumps(data, indent=2, sort_keys=True)
        request = Request(
            url=url,
            headers=headers,
            data=payload.encode('utf8')
        )

        self.log_request(uri, headers, payload)

        if self.dry_run:
            self.logger.info('Not sending because --dry-run.')
            return

        try:
            response = urlopen(
                request,
                timeout=self.timeout,
            )
        # voidspace.org.uk/python/articles/urllib2.shtml#handling-exceptions
        except HTTPError as e:
            self.logger.error('< The server could not fulfill the request')
            self.logger.debug('HTTP error', exc_info=True)
            self.log_response(e, level=logging.ERROR)

            raise ClientHTTPError(e.code)

        except URLError as e:  # Connection error.
            try:
                code, reason = e.reason.args
            except ValueError:
                code, reason = None, str(e)
            if reason == 'Operation now in progress':
                error_msg = 'request timed out (--timeout=%.2f)' % self.timeout
            else:
                error_msg = reason
            self.logger.error('Unable to reach the API server: %s', error_msg)
            self.logger.debug('URL error (connection error)', exc_info=0)

            raise ClientConnectionError(error_msg)

        except Exception:
            raise  # Unexpected error, not handled here.
        else:
            self.log_response(response, level=logging.DEBUG)
