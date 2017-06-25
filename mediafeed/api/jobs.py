from ..jobs import job_manager
from .server import api


__all__ = ('jobs_list',)


@api.get('/jobs')
def jobs_list():
    return job_manager.to_dict()
