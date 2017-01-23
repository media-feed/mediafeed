from ..errors import NotFound


class ModuleNotFound(NotFound):
    type = 'module'


class ModuleProcessError(Exception):
    def __init__(self, module_id, function_name, url=None, options=None):
        self.module_id = module_id
        self.function_name = function_name
        self.url = url
        if url is None:
            self.args = 'Module %s: Erro em %s' % (module_id, function_name),
        else:
            self.args = 'Module %s: Erro em %s de "%s" (opções: %r)' % (module_id, function_name, url, options),


class ModuleProcessExitError(Exception):
    def __init__(self, exit_status):
        self.exit_status = exit_status
        self.args = 'Exit status %d' % exit_status,
