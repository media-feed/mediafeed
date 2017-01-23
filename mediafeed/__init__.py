from logging import getLogger


__version__ = '0.1.dev0'


logger = getLogger('mediafeed')


def init():
    from .commands import load_commands
    from .modules import load_modules

    logger.info('Iniciando Media Feed')
    load_modules()
    load_commands()
