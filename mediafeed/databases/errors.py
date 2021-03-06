from ..errors import NotFound


class GroupNotFound(NotFound):
    type = 'group'


class SourceNotFound(NotFound):
    type = 'source'


class ItemNotFound(NotFound):
    type = 'item'
