import os
from shutil import rmtree
from sqlalchemy import and_, or_
from tabulate import tabulate

from ..cli.parser import subparsers
from ..databases import Session, Source, Item, get_group, get_groups_ids_recursive, get_item
from .api import api
from .utils import bool_to_str, str_to_bool, read_group, read_source


__all__ = ('parser_item', 'item_list', 'item_show', 'item_viewed', 'item_remove', 'item_download', 'item_removemedia')


parser_item = subparsers.add_parser('item',
                                    help='commandos de itens da fonte de mídia')
subparsers_item = parser_item.add_subparsers(dest='_action', metavar='ACTION')


def item_to_json(item):
    sources = [(source.id, source.name) for source in item.sources]
    return {
        'module_id': item.module_id,
        'id': item.id,
        'sources_id': [id for id, _ in sources],
        'sources_names': [name for _, name in sources],
        'url': item.url,
        'datetime': str(item.datetime),
        'timestamp': item.timestamp,
        'name': item.name,
        'thumbnail_url': item.thumbnail_url,
        'media_url': item.media_url,
        'text': item.text,
        'viewed': item.viewed,
        'medias': [media.filename for media in item.medias],
    }


def print_item(item):
    print('Module = %s' % item['module_id'])
    print('ID = %s' % item['id'])
    print('Sources = %s' % ', '.join(sorted(item['sources_names'], key=lambda x: x.lower())))
    print('URL = %s' % item['url'])
    print('Date = %s' % item['datetime'])
    print('Name = %s' % item['name'])
    print('Thumbnail URL = %s' % item['thumbnail_url'])
    print('Media URL = %s' % item['media_url'])
    print('Medias = %s' % ', '.join(sorted(item['medias'], key=lambda x: x.lower())))
    print('Viewed = %s' % bool_to_str(item['viewed']))
    print()
    print(item['text'])


def print_item_table(items):
    print(tabulate([[
        item['module_id'],
        item['id'],
        item['datetime'],
        ', '.join(sorted(item['sources_names'], key=lambda x: x.lower())),
        item['url'],
        item['name'],
        bool_to_str(item['viewed']),
        bool_to_str(item['medias']),
    ] for item in sorted(items, key=lambda x: x['timestamp'])],
        headers=['Module', 'ID', 'Date', 'Sources', 'URL', 'Name', 'Viewed', 'Media']))


# Commands

parser_item_list = subparsers_item.add_parser('list',
                                              help='lista itens')
parser_item_list.set_defaults(_output=print_item_table)
parser_item_list.add_argument('--group', dest='groups', action='append', type=read_group,
                              help='')
parser_item_list.add_argument('--recursive', action='store_true',
                              help='')
parser_item_list.add_argument('--source', dest='sources', action='append', type=read_source,
                              help='')
parser_item_list.add_argument('--viewed', action='store_true', default=None,
                              help='')
parser_item_list.add_argument('--no-viewed', dest='viewed', action='store_false', default=None,
                              help='')
parser_item_list.add_argument('--media', action='store_true', default=None,
                              help='')
parser_item_list.add_argument('--no-media', dest='media', action='store_false', default=None,
                              help='')


@api('GET', '/item', multiple='items')
def item_list(groups=None, recursive=None, sources=None, viewed=None, media=None, db=None):
    if recursive is not None and isinstance(recursive, str):
        recursive = str_to_bool(recursive)
    if viewed is not None and isinstance(viewed, str):
        viewed = str_to_bool(viewed)
    if media is not None and isinstance(media, str):
        media = str_to_bool(media)
    if db is None:
        db = Session()
    if groups is None:
        groups = []
    if recursive:
        groups = {g for group in groups for g in get_groups_ids_recursive(db, group)}
    if sources is None:
        sources = []
    for group in groups:
        sources += [(source.module_id, source.id) for source in get_group(db, group).sources]
    if groups and not sources:
        return []
    items = db.query(Item)
    if viewed is not None:
        items = items.filter(Item.viewed == viewed)
    if sources:
        items = items.join(Source.items).filter(or_(and_(Source.module_id == source[0], Source.id == source[1])
                                                    for source in sources))
    items = items.all()
    if media is not None:
        items = [item for item in items if bool(item.medias) == media]
    return [item_to_json(item) for item in items]


parser_item_show = subparsers_item.add_parser('show',
                                              help='mostra informações do item')
parser_item_show.set_defaults(_output=print_item)
parser_item_show.add_argument('module',
                              help='ID do módulo')
parser_item_show.add_argument('id',
                              help='ID do item')


@api('GET', '/item/<module>/<id>')
def item_show(module, id, db=None):
    if db is None:
        db = Session()
    return item_to_json(get_item(db, module, id))


parser_item_viewed = subparsers_item.add_parser('viewed',
                                                help='altera o estado de visualizado')
parser_item_viewed.set_defaults(_output=print_item)
parser_item_viewed.add_argument('module',
                                help='ID do módulo')
parser_item_viewed.add_argument('id',
                                help='ID do item')
parser_item_viewed.add_argument('--no-viewed', dest='viewed', action='store_false',
                                help='marca item como não visto')


@api('POST', '/item/<module>/<id>/viewed')
def item_viewed(module, id, viewed=True, db=None):
    if db is None:
        db = Session()
    item = get_item(db, module, id)
    item.viewed = viewed
    db.commit()
    return item_to_json(item)


parser_item_download = subparsers_item.add_parser('download',
                                                  help='baixa mídias do item')
parser_item_download.add_argument('module',
                                  help='ID do módulo')
parser_item_download.add_argument('id',
                                  help='ID do item')
parser_item_download.add_argument('--options',
                                  help='opções do módulo para a URL')


def item_remove(module, id, db=None):
    if db is None:
        db = Session()
    item = get_item(db, module, id)
    if item.thumbnail:
        item.thumbnail.remove()
    rmtree(item.media_path)
    db.delete(item)
    db.commit()


@api('POST', '/item/<module>/<id>/media')
def item_download(module, id, options=None, db=None):
    if db is None:
        db = Session()
    item = get_item(db, module, id)
    if options is None:
        options = item.sources[0].options
    item.module.get_media(item.media_path, item.media_url, options)
    return {}


parser_item_mediaremove = subparsers_item.add_parser('removemedia',
                                                     help='remove mídias do item')
parser_item_mediaremove.add_argument('module',
                                     help='ID do módulo')
parser_item_mediaremove.add_argument('id',
                                     help='ID do item')
parser_item_mediaremove.add_argument('--filename',
                                     help='nome da mídia')


@api('DELETE', '/item/<module>/<id>/media')
@api('DELETE', '/item/<module>/<id>/media/<filename:path>')
def item_removemedia(module, id, filename=None, db=None):
    if db is None:
        db = Session()
    item = get_item(db, module, id)
    if filename is None:
        rmtree(item.media_path)
    else:
        for media in item.medias:
            if media.filename == filename:
                os.remove(media.path)
    return {}
