class ActionNotImplemented(Exception):
    def __init__(self, method):
        self.args = 'Método "%s" não implementado neste módulo' % method,
