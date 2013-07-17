"""
opbeatcli.credentials
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Opbeat, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import os
from datetime import datetime
import ConfigParser
from ConfigParser import SafeConfigParser


date_format = '%Y-%m-%d %H:%M:%S'


def get_default_filename():
    return os.path.expanduser('~/.opbeat')


def get_config(filename):
    filename = filename or get_default_filename()

    config = SafeConfigParser()
    config.readfp(open(filename))
    return config


def save_config(filename, config):
    filename = filename or get_default_filename()
    with open(filename, 'wb') as configfile:
        config.write(configfile)


def load_credentials(filename=None):
    try:
        config = get_config(filename)

        return {
            'access_token': config.get('credentials', 'access_token'),
            'refresh_token': config.get('credentials', 'refresh_token'),
            'expires': datetime.strptime(
                config.get('credentials', 'expires'), date_format)
        }
    except:
        return None


def clear_credentials(filename=None):
    filename = filename or get_default_filename()
    config = get_config(filename)
    config.remove_section('credentials')
    save_config(filename, config)


def save_credentials(access_token, refresh_token, expires, filename=None):
    filename = filename or get_default_filename()
    try:
        config = get_config(filename)
    except IOError:
        config = SafeConfigParser()

    try:
        config.add_section('credentials')
    except ConfigParser.DuplicateSectionError:
        pass

    config.set('credentials', 'access_token', access_token)
    config.set('credentials', 'refresh_token', refresh_token)
    config.set('credentials', 'expires', expires.strftime(date_format))

    save_config(filename, config)
