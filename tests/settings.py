# Testing auth settings.
#
# This file is both valid Python and Bash script.
#
# Python: Import auth args:
#     from .setttings import AUTH_ARGS
#
# Bash: set environment variables with auth info for `opbeat':
#   $ . settings.py
#   $ opbeat deployment --component path:.


# 'Opbeat Tests' / 'Opbeat CLI Testing'
OPBEAT_ORGANIZATION_ID='43764a32d9c24333a695c19071db9b90'
OPBEAT_APP_ID='ee676def91'
OPBEAT_SECRET_TOKEN='ee3beb6a7ca5684c87ab179a0bf5538cf9079fbd'


AUTH_ARGS=['-o',OPBEAT_ORGANIZATION_ID,'-a',OPBEAT_APP_ID,'-t',OPBEAT_SECRET_TOKEN,]
