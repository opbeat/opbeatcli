
import requests
import json
import os
from datetime import datetime, timedelta

import logging

from opbeat.command import CommandBase
from opbeat.credentials import save_tokens
from opbeat.utils import say
from opbeat.conf.defaults import CLIENT_ID

class LoginError(Exception):
	pass


class LoginCommand(CommandBase):
	name = "login"
	description = "Log in to the Opbeat platform."

	def add_args(self):
		self.parser.add_argument('--client-id', help="Override oauth client id (you probably don't need this)", default=CLIENT_ID)

	def run(self, args):
		self.logger.info("In order to proceed, point you browser to: ")
		self.logger.info(" https://opbeat.com/oauth2/cli/")
		self.logger.info("After you have authorized, you will be given a code.")
		self.logger.info("Paste it here - now.")

		try:
			grant_code = raw_input('Code: ')
		except KeyboardInterrupt:
			self.logger.debug("Canceled")
		else:
			self.logger.debug('Logging in...')
			try:
				result = self.exchange_code_for_token(args.server, grant_code, args.client_id)
				save_tokens(access_token=result['access_token'], refresh_token=result['refresh_token'], expires=datetime.now() + timedelta(seconds=result['expires_in']))
			except LoginError, ex:
				self.logger.error(ex)
			else:
				say("logged in")
				self.logger.debug('Success!')

	def exchange_code_for_token(self, server, code,client_id):
		url = server + "/oauth2/access_token/"
		data = {
			'code':code,
			'grant_type':'authorization_code',
			'client_id':client_id,
		}
		self.logger.debug("Exchanging code for access token")
		self.logger.debug("Sending %s", data)
		request = requests.post(url, data=data,verify=True)
		result = json.loads(request.content)
		self.logger.debug("Got: %s", result)
		if 'error' in result:
				raise LoginError(result['error'])

		return result


command = LoginCommand

# def send_test_message(client, *args):
# 	print 'Sending a test message...',
# 	ident = client.get_ident(client.captureMessage(
# 		message='This is a test message generated using ``opbeat_python test``',
# 		data={
# 			'culprit': 'opbeat_python.scripts.runner',
# 			'logger': 'opbeat_python.test',
# 			'http': {
# 				'method': 'GET',
# 				'url': 'http://example.com',
# 			}
# 		},
# 		level=logging.INFO,
# 		stack=True,
# 		extra={
# 			'user': pwd.getpwuid(os.geteuid())[0],
# 			'loadavg': os.getloadavg(),
# 		}
# 	))

# 	if client.state.did_fail():
# 		print 'error!'
# 		return False

# 	print 'success!'
# 	print
	
