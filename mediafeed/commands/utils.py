from ..databases import Session, Group
from ..databases.errors import GroupNotFound


def bool_to_str(value):
    if value:
        return 'Sim'
    return 'Não'


def str_to_bool(value):
    return value.lower() in {'1', 'true'}


def read_group(arg):
    path = arg.split('/')
    db = Session()
    group = db.query(Group.id).filter(Group.parent_id == None, Group.name == path[0]).first()
    if group is None:
        raise GroupNotFound(arg)
    for i in range(1, len(path)):
        group = db.query(Group.id).filter(Group.parent_id == group[0], Group.name == path[i]).first()
        if group is None:
            raise GroupNotFound(arg)
    return group[0]


def read_source(arg):
    return arg.split(':', 1)
