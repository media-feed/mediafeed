class NotFound(Exception):
    type = ''

    def __init__(self, id):
        self.id = id
        self.args = ('%s "%s" não encontrado' % (self.type.title(), self.id)).strip(),
