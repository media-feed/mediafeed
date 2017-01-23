import os
from glob import glob
from logging import getLogger
from traceback import format_exc

from .errors import ModuleNotFound
from .models import Module


logger = getLogger('mediafeed.modules')


_modules = {}


def load_modules(paths=None):
    logger.info('Carregando módulos')
    global _modules
    _modules = {}
    if paths is None:
        paths = os.environ['PATH'].split(os.pathsep)

    globs = [(os.path.basename(module)[17:], module)
             for path in paths
             for module in glob(os.path.join(path, 'mediafeed-module-*'))]

    for module_id, module_path in globs:
        if module_id in _modules:
            continue
        try:
            _modules[module_id] = Module(module_id, module_path)
            logger.debug('%s carregado' % module_id)
        except Exception as e:
            logger.error(e)
            logger.debug(format_exc())


def get_modules(url=None, options=None):
    modules = _modules.values()
    if url is not None:
        modules = {module for module in modules if module.is_valid_url(url, options)}
    return modules


def get_module(id):
    try:
        return _modules[id]
    except KeyError:
        raise ModuleNotFound(id)
