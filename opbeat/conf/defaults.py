"""
opbeat.conf.defaults
~~~~~~~~~~~~~~~~~~~

Represents the default values for all Opbeat settings.

:copyright: (c) 2011-2012 Opbeat
"""

import os
import os.path
import socket

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))

# This should be the schema+host of the Opbeat server
SERVER = 'https://www.opbeat.com'

# Error API path
ERROR_API_PATH = '/api/v1/error/'

# Deployment Tracking API path
DEPLOYMENT_API_PATH = '/api/v1/deployment/'

TIMEOUT = 5
