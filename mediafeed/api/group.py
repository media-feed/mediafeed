from bottle import request

from ..commands import group as cmd
from ..utils import read_bool, read_int
from .server import api


__all__ = ('group_list', 'group_show', 'group_add', 'group_edit', 'group_remove')


@api.get('/groups')
def group_list():
    return {
        'groups': cmd.list_groups(
            root_id=read_int(request.query.get('root_id')),
            recursive=read_bool(request.query.get('recursive'), True),
        ),
    }


@api.get('/groups/<id>')
def group_show(id):
    return cmd.show_group(
        id,
        recursive=read_bool(request.query.get('recursive'), False),
    )


@api.post('/groups')
def group_add():
    return cmd.add_group(
        request.json['name'],
        parent_id=request.json.get('parent_id'),
    )


@api.post('/groups/<id>')
def group_edit(id):
    return cmd.edit_group(
        id,
        parent_id=request.json.get('parent_id', 0),
        name=request.json.get('name'),
    )


@api.delete('/groups/<id>')
def group_remove(id):
    return cmd.remove_group(id)
