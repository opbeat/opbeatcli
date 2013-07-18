"""
Default values for all Opbeat settings.

"""

import os
import socket


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# This should be the schema+host of the Opbeat server
SERVER = 'https://opbeat.com'

# Deployment Tracking API path
DEPLOYMENT_API_URI = \
    '/api/v1/organizations/{organization_id}/apps/{app_id}/deployments/'

TIMEOUT = 10

CLIENT_ID = '0bbfbe8fc567d3db93de'

HOSTNAME = socket.gethostname()
