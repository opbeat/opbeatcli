import logging
import version
from conf import defaults
from utils import json

import urllib2
from urlparse import urlparse

__all__ = ('Client',)

class Client(object):
	"""
	The base opbeat client, which handles communication over the
	with Opbeat servers.

	Will read default configuration from the environment variable
	``OPBEAT_PROJECT_ID`` and ``OPBEAT_API_KEY`` if available.

	>>> from opbeat import Client

	>>> # Read configuration from ``os.environ['OPBEAT_PROJECT_ID']``
	>>> # and ``os.environ['OPBEAT_API_KEY']``
	>>> client = Client()

	>>> # Configure the client manually
	>>> client = Client(
	>>>     project='project_id',
	>>>     api_key='api_key'
	>>> )

	>>> # Send some information
	>>> client.send(**data)

	"""
	logger = logging.getLogger('opbeat.client')
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	logger.addHandler(ch)

	protocol_version = '1.0'

	def __init__(self, access_token, server, project_id = None):
		self.access_token = access_token
		self.server = server
		self.project_id = project_id

		if not (access_token and server):
			msg = 'Missing configuration for client. Please see documentation.'
			raise TypeError(msg)

	def send(self, data, url, auth_header=None):
		"""
		Serializes the message and passes the payload onto ``send_encoded``.
		"""

		if self.project_id and 'project_id' not in data:
			data['project_id'] = self.project_id


		message = self.encode(data)
		return self.send_encoded(message,url, auth_header=auth_header)

	def send_encoded(self, data, url, auth_header=None):
		"""
		Given an already serialized message, signs the message and passes the
		payload off to ``send_remote`` for each server specified in the servers
		configuration.
		"""

		# server = server or self.server
		# if not server:
		# 	warnings.warn('opbeat client has no remote servers configured')
		# 	return

		if not auth_header:
			access_token = self.access_token

			auth_header = "access_token %s" % (access_token)
	
		headers = {
			'Authorization': auth_header,
			'Content-Type': 'application/json',
			'User-Agent': 'opbeat/%s' % version.VERSION
		}

		# url =  "%s%s" % (self.server, url)

		self.send_remote(url=url, data=data, headers=headers)

	def encode(self, data):
		"""
		Serializes ``data`` into a raw string.
		"""
		return json.dumps(data).encode('zlib')

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
		try:
			self._send_remote(url=url, data=data, headers=headers)
		except Exception, e:
			if isinstance(e, urllib2.HTTPError):
				body = e.read()
				self.logger.error('Unable to reach Opbeat server: %s (url: %%s, body: %%s)' % (e,), url, body,
					exc_info=True, extra={'data': {'body': body, 'remote_url': url}})
			else:
				tmpl = 'Unable to reach Opbeat server: %s (url: %%s)'
				self.logger.error(tmpl % (e,), url, exc_info=True,
						extra={'data': {'remote_url': url}})
