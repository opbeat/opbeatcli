"""
opbeat.utils.json
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 Opbeat
:license: BSD, see LICENSE for more details.
"""

import datetime
import uuid
import os
import sys
import json


def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is one of "yes" or "no".
	"""
	valid = {"yes":True,   "y":True,  "ye":True,
			 "no":False,     "n":False}
	if default == None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "\
							 "(or 'y' or 'n').\n")


def say(words):
	"""
		This is really silly.
	"""
	if os.path.exists('/usr/bin/say'):
		os.system("/usr/bin/say %s" % words)

# copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
class BetterJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, uuid.UUID):
			return obj.hex
		elif isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
		elif isinstance(obj, (set, frozenset)):
			return list(obj)
		return super(BetterJSONEncoder, self).default(obj)


def better_decoder(data):
	return data


def dumps(value, **kwargs):
	return json.dumps(value, cls=BetterJSONEncoder, **kwargs)


def loads(value, **kwargs):
	return json.loads(value, object_hook=better_decoder)