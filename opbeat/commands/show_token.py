import requests
import json
import os
from datetime import datetime, timedelta

import logging

from opbeat.command import CommandBase
from opbeat.credentials import load_tokens


class ShowTokenCommand(CommandBase):
	name = "show_token"
	description = "Prints the saved access token to STDOUT."

	def run(self, args):
		try:
			self.logger.info(load_tokens()['access_token'])
		except Exception, ex:
			self.logger.error(ex)
			self.logger.error("Could not load credentials. Are you logged in?")

command = ShowTokenCommand

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
	
