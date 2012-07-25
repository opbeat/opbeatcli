from command import CommandBase
from credentials import save_tokens
import requests
import json
import os
from datetime import datetime, timedelta
from utils import say
import logging

CLIENT_ID = "0bbfbe8fc567d3db93de"

class LoginError(Exception):
	pass

def exchange_code_for_token(server, code):
	url = server + "/oauth2/access_token/"
	data = {
		'code':code,
		'grant_type':'authorization_code',
		'client_id':CLIENT_ID,
	}
	request = requests.post(url, data=data,verify=True)
	result = json.loads(request.content)

	if 'error' in result:
		raise LoginError(result['error'])

	return result

class LoginCommand(CommandBase):
	name = "login"
	description = "Log in to the Opbeat platform."

	def run(self, args):


		self.logger.info("In order to proceed, point you browser to: ")
		self.logger.info(" https://opbeat.com/oauth/cmdclient/")
		self.logger.info("After you have authorized, you will be given a code.")
		self.logger.info("Paste it here - now.")

		grant_code = raw_input('Code: ')

		self.logger.info('Logging in...')
		try:
			result = exchange_code_for_token(args.server, grant_code)
			save_tokens(access_token=result['access_token'], refresh_token=result['refresh_token'], expires=datetime.now() + timedelta(seconds=result['expires_in']))
		except LoginError, ex:
			print ex
		else:
			say("logged in")
			self.logger.info('Success!')

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
	
