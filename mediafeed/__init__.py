from logging import getLogger


__version__ = '0.1.dev0'


logger = getLogger('mediafeed')


def init():
    logger.info('Iniciando Media Feed...')
