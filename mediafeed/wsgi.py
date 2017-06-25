from . import init, start_background_jobs
from .api.server import application  # NOQA


init()
start_background_jobs()
