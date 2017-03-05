from logging import getLogger

from ..databases import Group, get_group, get_groups_root
from ..databases import Session
from .errors import CommandError


__all__ = ('list_groups', 'show_group', 'add_group', 'edit_group', 'remove_group')


logger = getLogger('mediafeed.commands.group')


def list_groups(root_id=None, recursive=True, db=None):
    logger.debug('list_groups root_id=%r recursive=%r' % (root_id, recursive))
    if db is None:
        db = Session()
    if root_id is not None:
        groups = [get_group(db, root_id)]
    else:
        groups = get_groups_root(db)
    return [group.to_dict(recursive=recursive) for group in groups]


def show_group(id, recursive=False, db=None):
    logger.debug('show_group id=%r recursive=%r' % (id, recursive))
    if db is None:
        db = Session()
    group = get_group(db, id)
    return group.to_dict(recursive=recursive)


def add_group(name, parent_id=None, db=None):
    logger.debug('add_group name=%r parent_id=%r' % (name, parent_id))
    if db is None:
        db = Session()
    if parent_id:
        parent = get_group(db, parent_id)
    else:
        parent = None
    group = Group(
        parent=parent,
        name=name,
    )
    db.add(group)
    db.commit()
    return group.to_dict()


def edit_group(id, parent_id=0, name=None, db=None):
    logger.debug('edit_group id=%r parent_id=%r name=%r' % (id, parent_id, name))
    if db is None:
        db = Session()
    group = get_group(db, id)
    if parent_id is None:
        group.parent_id = None
    elif parent_id:
        p = get_group(db, parent_id)
        while p:
            if p.id == id:
                raise CommandError('Loop na árvore de grupos')
            p = p.parent
        group.parent_id = parent_id
    if name:
        group.name = name
    db.commit()
    return group.to_dict()


def remove_group(id, db=None):
    logger.debug('remove_group id=%r' % id)
    if db is None:
        db = Session()
    group = get_group(db, id)
    db.delete(group)
    db.commit()
    return {}
