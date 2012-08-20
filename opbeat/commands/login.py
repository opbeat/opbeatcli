import requests
import json
import os
from datetime import datetime, timedelta

import logging

from opbeat.command import CommandBase
from opbeat.credentials import save_credentials, load_credentials
from opbeat.utils import say
from opbeat.conf.defaults import CLIENT_ID, SERVER

class LoginError(Exception):
	pass

def login(logger, server, client_id):
	"""
		Guides the user through the login process

		returns an access token on success.
	"""
	logger.info("In order to proceed, point you browser to: ")
	logger.info(" https://opbeat.com/oauth2/cli/")
	logger.info("After you have authorized, you will be given a code.")
	logger.info("Paste it here - now.")

	try:
		grant_code = raw_input('Code: ')
	except KeyboardInterrupt:
		logger.debug("Canceled")
		raise
	else:
		logger.debug('Logging in...')

		result = exchange_code_for_token(logger, server, client_id, grant_code)
		save_credentials(access_token=result['access_token'], refresh_token=result['refresh_token'], expires=datetime.now() + timedelta(seconds=result['expires_in']))
		return result['access_token']

def exchange_code_for_token(logger, server, client_id, code):
	url = server + "/oauth2/access_token/"
	data = {
		'code':code,
		'grant_type':'authorization_code',
		'client_id':client_id,
	}
	logger.debug("Exchanging code for access token")
	logger.debug("Sending %s", data)
	request = requests.post(url, data=data,verify=True)
	result = json.loads(request.content)
	logger.debug("Got %s", result)
	if 'error' in result:
			raise LoginError(result['error'])

	return result

class LoginCommand(CommandBase):
	name = "login"
	description = "Log in to the Opbeat platform."

	def add_args(self):
		self.parser.add_argument('--client-id', 
			help = "Override oauth client id (you probably don't need this)",
			default = os.environ.get('OPBEAT_CLIENT_ID', CLIENT_ID)
			)

	def run(self, args):
		try:
			login(self.logger, args.server, args.client_id)
		except LoginError, ex:
			logger.error(ex)
		else:
			say("logged in")
			logger.debug('Success!')

command = LoginCommand
