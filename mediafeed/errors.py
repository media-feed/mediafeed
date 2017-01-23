class NotFound(Exception):
    type = ''

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.args[0]

    @property
    def args(self):
        return ('%s "%s" não encontrado' % (self.type.title(), self.id)).strip(),
