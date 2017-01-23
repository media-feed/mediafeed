from logging import getLogger


__version__ = '0.1.dev0'


logger = getLogger('mediafeed')


def init():
    from .commands import load_commands

    logger.info('Iniciando Media Feed')
    load_commands()
