from bottle import request

from ..commands import source as cmd
from ..utils import read_bool, read_int
from .server import api


__all__ = ('source_list', 'source_show', 'source_add', 'source_edit', 'source_remove')


@api.get('/sources')
def source_list():
    return {
        'sources': cmd.list_sources(
            group_id=read_int(request.query.get('group_id', '0')),
            recursive=read_bool(request.query.get('recursive')),
            auto_download_media=read_bool(request.query.get('auto_download_media')),
            persist_thumbnails=read_bool(request.query.get('persist_thumbnails')),
            error=read_bool(request.query.get('error')),
        )
    }


@api.get('/sources/<module_id>/<id>')
def source_show(module_id, id):
    return cmd.show_source(module_id, id)


@api.post('/sources')
def source_add():
    return cmd.add_source(
        request.json['module_id'],
        request.json['url'],
        id=request.json.get('id'),
        group_id=request.json.get('group_id'),
        options=request.json.get('options'),
        name=request.json.get('name'),
        thumbnail_url=request.json.get('thumbnail_url'),
        web_url=request.json.get('web_url'),
        auto_download_media=request.json.get('auto_download_media'),
        persist_thumbnails=request.json.get('persist_thumbnails'),
    )


@api.post('/sources/<module_id>/<id>')
def source_edit(module_id, id):
    return cmd.edit_source(
        module_id,
        id,
        group_id=request.json.get('group_id', 0),
        url=request.json.get('url'),
        options=request.json.get('options'),
        name=request.json.get('name'),
        thumbnail_url=request.json.get('thumbnail_url'),
        web_url=request.json.get('web_url'),
        auto_download_media=request.json.get('auto_download_media'),
        persist_thumbnails=request.json.get('persist_thumbnails'),
    )


@api.delete('/sources/<module_id>/<id>')
def source_remove(module_id, id):
    return cmd.remove_source(module_id, id)
