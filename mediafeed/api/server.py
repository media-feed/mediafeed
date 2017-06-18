import os

from bottle import Bottle
from whitenoise import WhiteNoise

from ..settings import DATA_PATH


api = Bottle()

application = WhiteNoise(api)
application.add_files(os.path.join(DATA_PATH, 'thumbnails'), prefix='thumbnails/')
application.add_files(os.path.join(DATA_PATH, 'medias'), prefix='medias/')
