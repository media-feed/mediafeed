from bottle import Bottle, request, response
from logging import getLogger

from ..errors import NotFound
from .errors import CommandNotFound


logger = getLogger('mediafeed.commands')


_app = None
_api_commands = {}


def response_http(func, multiple):
    def decorate(**kwargs):
        for key, value in request.query.items():
            kwargs[key] = value
        for key, value in request.forms.items():
            kwargs[key] = value

        try:
            ret = func(**kwargs)
        except NotFound as e:
            response.status = 404
            return {
                'error': str(e),
            }
        except Exception as e:
            response.status = 500
            return {
                'error': str(e),
            }

        if multiple:
            return {multiple: ret}
        return ret
    return decorate


def api(method, url, multiple=None):
    def decorate(func):
        _api_commands[func.__name__] = method, url, func, multiple
        return func
    return decorate


def get_command(name):
    try:
        _, _, func, _ = _api_commands[name]
        return func
    except KeyError:
        raise CommandNotFound(name)


def get_app():
    return _app


def load_commands():
    logger.info('Carregando comandos')
    global _app
    _app = Bottle()
    for method, url, func, multiple in _api_commands.values():
        _app.route(method=method, path=url, name=func.__name__,
                   callback=response_http(func, multiple))
        logger.debug('%s carregado' % func.__name__)
