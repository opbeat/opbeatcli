"""
opbeatcli.conf.defaults
~~~~~~~~~~~~~~~~~~~

Represents the default values for all Opbeat settings.

:copyright: (c) 2011-2012 Opbeat
"""

import os
import os.path
import socket

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# This should be the schema+host of the Opbeat server
SERVER = 'https://opbeat.com'

# Deployment Tracking API path
DEPLOYMENT_API_PATH = '/api/v1/organizations/{0}/apps/{1}/deployments/'

TIMEOUT = 10

CLIENT_ID = "0bbfbe8fc567d3db93de"

HOSTNAME = socket.gethostname()
