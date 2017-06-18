from bottle import request

from ..commands import module as cmd
from .server import api


__all__ = ('module_list', 'module_show', 'source_metadata')


@api.get('/modules')
def module_list():
    return {
        'modules': cmd.list_modules(
            url=request.query.get('url'),
            options=request.query.get('options'),
        ),
    }


@api.get('/modules/<id>')
def module_show(id):
    return cmd.show_module(id)


@api.get('/sources/metadata/<module_id>/<url:path>')
def source_metadata(module_id, url):
    return cmd.get_source_metadata(
        module_id,
        url,
        options=request.query.get('options'),
    )
