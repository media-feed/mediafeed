from logging import getLogger


__version__ = '0.1.dev0'


logger = getLogger('mediafeed')


def init():
    from .databases import initdb
    from .modules import load_modules

    logger.info('Iniciando Media Feed...')
    load_modules()
    initdb()


def start_background_jobs():
    from .jobs import job_manager

    logger.info('Inicinando tarefas em segundo plano')
    job_manager.start()


def stop_background_jobs():
    from .jobs import job_manager

    logger.info('Parando tarefas em segundo plano')
    job_manager.stop()
