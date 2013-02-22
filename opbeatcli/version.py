
try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('opbeatcli').version
except Exception, e:
    VERSION = 'unknown'

PROTOCOL_VERSION = "v1"