from bottle import request

from ..commands import item as cmd
from ..utils import read_bool
from .server import api


__all__ = ('item_list', 'item_show', 'item_edit')


@api.get('/items')
def item_list():
    return {
        'items': cmd.list_items(
            groups_id={int(group_id) for group_id in request.query.getlist('groups_id')},
            recursive=read_bool(request.query.get('recursive'), False),
            sources_id={tuple(source_id.split(':', 1)) for source_id in request.query.getlist('sources_id')},
            viewed=read_bool(request.query.get('viewed')),
            media=read_bool(request.query.get('media')),
        ),
    }


@api.get('/items/<module_id>/<id>')
def item_show(module_id, id):
    return cmd.show_item(module_id, id)


@api.post('/items/<module_id>/<id>')
def item_edit(module_id, id):
    return cmd.edit_item(
        module_id,
        id,
        viewed=request.json.get('viewed'),
    )
