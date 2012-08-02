import requests
import json
import os
from datetime import datetime, timedelta

import logging

from opbeat.command import CommandBase
from opbeat.credentials import load_credentials


class ShowTokenCommand(CommandBase):
	name = "show_token"
	description = "Prints the saved access token to STDOUT."

	def run(self, args):
		try:
			self.logger.info(load_credentials()['access_token'])
		except Exception, ex:
			self.logger.error(ex)
			self.logger.error("Could not load credentials. Are you logged in?")

command = ShowTokenCommand
