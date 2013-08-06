import logging

logger = logging.getLogger('opbeat')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(name)s:%(levelname)s: %(message)s')
)
logger.addHandler(handler)


if not hasattr(logger, 'getChild'):
    logger.getChild = lambda name: logging.getLogger(
        '.'.join([logger.name, name]))
