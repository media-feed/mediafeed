from bottle import request

from ..commands import item as cmd
from ..jobs import job_manager
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


@api.post('/item/<module_id>/<id>/media')
def item_media_download(module_id, id):
    json = request.json or {}
    options = json.get('options')
    job_manager.add_job('download_media', {
        'module_id': module_id,
        'item_id': id,
        'options': options,
    })
    return {}


@api.delete('/item/<module_id>/<id>/media')
def item_media_remove(module_id, id):
    return cmd.remove_media(
        module_id,
        id,
        filename=request.json.get('filename'),
    )
