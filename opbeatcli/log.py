import logging

root_logger = logging.getLogger('opbeatcli.errors')
root_logger.addHandler(logging.StreamHandler())
