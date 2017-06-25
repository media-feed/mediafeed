import os


DATA_PATH = os.environ.get('MEDIAFEED_DATA', os.path.expanduser(os.path.join('~', '.mediafeed', 'data')))
os.makedirs(DATA_PATH, exist_ok=True)

DATABASE_URL = 'sqlite:///%s/db.sqlite3' % DATA_PATH

WORKERS_DOWNLOAD_MEDIA = int(os.environ.get('MEDIAFEED_WORKERS_DOWNLOAD_MEDIA', 1))
WORKERS_UPDATE_ITEMS = int(os.environ.get('MEDIAFEED_WORKERS_UPDATE_ITEMS', 1))
