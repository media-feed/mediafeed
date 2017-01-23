from ..errors import NotFound


class CommandError(Exception):
    pass


class CommandNotFound(NotFound):
    type = 'command'
