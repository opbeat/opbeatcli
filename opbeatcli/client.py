"""
Opbeat log API client.

"""
import logging

import requests

from opbeatcli import __version__
from opbeatcli.utils import json
from opbeatcli import settings
from opbeatcli.exceptions import (
    ClientConnectionError,
    ClientHTTPError
)


class OpbeatClient(object):
    """
    The Opbeat client, which handles communication with the
    Opbeat servers.

    """
    def __init__(self, secret_token, organization_id, app_id,
                 logger, server=settings.SERVER,
                 timeout=settings.TIMEOUT, dry_run=False):

        self.server = server
        self.secret_token = secret_token
        self.organization_id = organization_id
        self.app_id = app_id

        self.timeout = timeout
        self.logger = logger
        self.dry_run = dry_run

        logger.info('Opbeat client configuration:')
        for k in ['server', 'organization_id', 'app_id']:
            logger.info('  %16s: %s' % (k, getattr(self, k)))

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

        data = dict(
            data,
            organization_id=self.organization_id,
            app_id=self.app_id
        )

        payload = json.dumps(data, indent=2, sort_keys=True)

        self.logger.debug('> Server: %s', self.server)
        self.logger.debug('> HTTP/1.1 POST %s', uri)
        self.logger.debug('> %s', payload)

        if self.dry_run:
            self.logger.info('Not sending because --dry-run.')
            return

        try:
            response = requests.post(
                url=url,
                data=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.Timeout as e:
            self.logger.error(
                'connection error: request timed out'
                ' (--timeout=%f)',
                self.timeout
            )
            self.logger.debug('request failed', exc_info=True)
            raise ClientConnectionError(e)
        except requests.ConnectionError as e:
            self.logger.error(
                'connection error: Unable to reach Opbeat server: %s',
                url,
            )
            self.logger.debug('request failed', exc_info=True)
            raise ClientConnectionError(e)
        except Exception:
            raise  # Unexpected error, not handled here.
        else:

            def log_response(level):
                self.logger.log(
                    level,
                    '< HTTP %d %s',
                    response.status_code,
                    response.reason
                )
                self.logger.log(level, '< %s', response.text)

            if response.status_code >= 400:
                log_response(logging.ERROR)
                raise ClientHTTPError(response.status_code)

            else:
                log_response(logging.DEBUG)
                return json.loads(response.text)
