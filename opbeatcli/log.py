import logging

logger = logging.getLogger('opbeat')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(name)s:%(levelname)s: %(message)s')
)
logger.addHandler(handler)
