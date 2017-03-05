from logging import getLogger

from ..modules import get_module, get_modules


__all__ = ('list_modules', 'show_module', 'get_source_metadata')


logger = getLogger('mediafeed.commands.module')


def list_modules(url=None, options=None):
    logger.debug('list_modules url=%r options=%r' % (url, options))
    modules = get_modules(url, options)
    return [module.to_dict() for module in modules]


def show_module(id):
    logger.debug('show_module id=%r' % id)
    module = get_module(id)
    return module.to_dict()


def get_source_metadata(module_id, url, options=None):
    logger.debug('get_source_metadata module_id=%r url=%r options=%r' % (module_id, url, options))
    module = get_module(module_id)
    return module.get_source_metadata(url, options)
