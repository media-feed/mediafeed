from ..errors import NotFound


class ModuleNotFound(NotFound):
    type = 'module'


class ModuleProcessError(Exception):
    def __init__(self, module, function, url=None, options=None):
        self.module = module
        self.function = function
        self.url = url
        self.options = options
        if url is None:
            self.args = 'Module %s: Erro em %s' % (module.id, function),
        else:
            self.args = 'Module %s: Erro em %s de "%s" (opções: %r)' % (module.id, function, url, options),


class ModuleProcessStatusError(Exception):
    def __init__(self, status):
        self.status = status
        self.args = 'Exit status %d' % status,
