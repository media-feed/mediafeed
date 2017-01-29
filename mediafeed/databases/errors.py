from ..errors import NotFound


class GroupNotFound(NotFound):
    type = 'group'
