
try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('opbeat_python').version
except Exception, e:
    VERSION = 'unknown'

PROTOCOL_VERSION = "v0"