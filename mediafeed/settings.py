import os


DATA_PATH = os.environ.get('MEDIAFEED_DATA', os.path.expanduser(os.path.join('~', '.mediafeed', 'data')))
os.makedirs(DATA_PATH, exist_ok=True)

DAEMON_PORT = int(os.environ.get('MEDIAFEED_PORT', 5447))
