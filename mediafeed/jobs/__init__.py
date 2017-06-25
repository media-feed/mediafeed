import os

from logging import getLogger
from simpleworker import WorkerManager

from ..commands import download_media, update_items
from ..settings import DATA_PATH, WORKERS_DOWNLOAD_MEDIA, WORKERS_UPDATE_ITEMS


__all__ = ('job_manager',)


def make_worker(cmd):
    def worker(name, queue):
        log = getLogger('mediafeed.jobs.%s' % name)
        log.info('Iniciando worker')
        while True:
            job = queue.get()
            if job is None:
                log.info('Parando worker')
                return
            try:
                log.info('Executando %r' % job)
                cmd(**job)
            except Exception as e:
                log.error(e)
            queue.done(job)
    return worker


job_manager = WorkerManager(path=os.path.join(DATA_PATH, 'tasks'))
job_manager.register('download_media', WORKERS_DOWNLOAD_MEDIA, make_worker(download_media))
job_manager.register('update_items', WORKERS_UPDATE_ITEMS, make_worker(update_items))
