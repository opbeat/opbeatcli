"""
opbeatcli.client
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.

Very inspired by the Client in the sentry/raven project.
"""


import logging
import version
from opbeatcli.conf import defaults
from opbeatcli.utils import json

import urllib2
from urlparse import urlparse

__all__ = ('Client',)

class Client(object):
	"""
	The base Opbeat client, which handles communication with the
	Opbeat servers.

	Will read default configuration from the environment variable
	``OPBEAT_ORGANIZATION_ID``, ``OPBEAT_APP_ID``, ``OPBEAT_SECRET_TOKEN``
	if available.

	>>> from opbeatcli import Client

	>>> # Configure the client
	>>> client = Client(
	>>>     organization_id='org_id',
	>>>     app_id='app_id'
	>>>     secret_token='secret_token'
	>>> )

	>>> # Send some information
	>>> client.send(**data)

	"""
	def __init__(self, logger,
		organization_id, app_id, secret_token, server,
		timeout=None, dry_run=False):
		
		self.organization_id = organization_id
		self.app_id = app_id

		self.secret_token = secret_token

		self.timeout = timeout or defaults.TIMEOUT
		self.logger = logger
		self.dry_run = dry_run

		self.server = server

		if not (secret_token and server):
			msg = 'Missing configuration for client. Please see documentation.'
			raise TypeError(msg)

	def send(self, data, url, auth_header=None):
		"""
		Serializes the message and passes the payload onto ``send_encoded``.
		"""

		if self.organization_id and 'organization_id' not in data:
			data['organization_id'] = self.organization_id

		if self.app_id and 'app_id' not in data:
			data['app_id'] = self.app_id

		message = self.encode(data)
		return self.send_encoded(message, url, auth_header=auth_header)

	def send_encoded(self, data, url, auth_header=None):
		"""
		Given an already serialized message, signs the message and passes the
		payload off to ``send_remote`` for each server specified in the servers
		configuration.
		"""

		if not auth_header:
			secret_token = self.secret_token

			auth_header = "Bearer %s" % (secret_token)

		headers = {
			'Authorization': auth_header,
			'Content-Type': 'application/json',
			'User-Agent': 'opbeatcli/%s' % version.VERSION
		}

		self.send_remote(url=url, data=data, headers=headers)

	def encode(self, data):
		"""
		Serializes ``data`` into a raw string.
		"""
		return json.dumps(data)

	def decode(self, data):
		"""
		Unserializes a string, ``data``.
		"""
		return json.loads(data.decode('zlib'))

	def _send_remote(self, url, data, headers={}):
		parsed = urlparse(url)
		transport = self._registry.get_transport(parsed)
		return transport.send(data, headers)

	def send_remote(self, url, data, headers={}):
		self.logger.debug("Sending: %s", data)

		if self.dry_run:
			return None

		try:
			"""
			Sends a request to a remote webserver using HTTP POST.
			"""
			req = urllib2.Request(url, headers=headers)
			response = urllib2.urlopen(req, data, self.timeout).read()

			self.logger.debug("Got: %s", response)
			return response
		except Exception, e:
			if isinstance(e, urllib2.HTTPError):
				body = e.read()
				self.logger.error('Unable to reach Opbeat server: %s (url: %%s, body: %%s)' % (e,), url, body,
					exc_info=True)
			else:
				tmpl = 'Unable to reach Opbeat server: %s (url: %%s)'
				self.logger.error(tmpl % (e,), url, exc_info=True)
