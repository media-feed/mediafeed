import os

from bottle import Bottle, response
from whitenoise import WhiteNoise

from ..settings import DATA_PATH


api = Bottle()


@api.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE'


application = WhiteNoise(api)
application.add_files(os.path.join(DATA_PATH, 'thumbnails'), prefix='thumbnails/')
application.add_files(os.path.join(DATA_PATH, 'medias'), prefix='medias/')
