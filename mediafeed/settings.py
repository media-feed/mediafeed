import os


DATA_PATH = os.environ.get('MEDIAFEED_DATA', os.path.expanduser(os.path.join('~', '.mediafeed', 'data')))
os.makedirs(DATA_PATH, exist_ok=True)

DATABASE_URL = 'sqlite:///%s/db.sqlite3' % DATA_PATH
