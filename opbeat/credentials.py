"""
opbeat.credentials
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from ConfigParser import SafeConfigParser
from datetime import datetime
date_format = "%Y-%m-%d %H:%M:%S"
import os

def get_default_filename():
	return os.path.expanduser("~/.opbeat")

def get_config(filename):
	filename = filename or get_default_filename()

	config = SafeConfigParser()
	config.readfp(open(filename))
	return config

def save_config(filename, config):
	filename = filename or get_default_filename()
	with open(filename, 'wb') as configfile:
		config.write(configfile)



def load_tokens(filename = None):
	config = get_config(filename)

	return {
		'access_token': config.get('credentials','access_token'),
		'refresh_token': config.get('credentials','refresh_token'),
		'expires': datetime.strptime(config.get('credentials','expires'), date_format)
		}

def save_tokens(access_token, refresh_token, expires, filename = None):
	filename = filename or get_default_filename()
	try:
		config = get_config(filename)
	except IOError:
		config = SafeConfigParser()
		config.add_section("credentials")

	config.set('credentials','access_token', access_token)
	config.set('credentials','refresh_token', refresh_token)
	config.set('credentials','expires', expires.strftime(date_format))

	save_config(filename, config)