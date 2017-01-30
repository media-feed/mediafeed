from tabulate import tabulate

from ..cli.parser import subparsers
from ..databases import Session, Source, get_group, get_groups_ids_recursive, get_source
from ..modules import get_module
from .api import api
from .item import item_remove
from .utils import bool_to_str, str_to_bool, read_group


__all__ = ('parser_source', 'source_list', 'source_show', 'source_add', 'source_edit', 'source_remove')


parser_source = subparsers.add_parser('source',
                                      help='comandos de fontes de mídia')
subparsers_source = parser_source.add_subparsers(dest='_action', metavar='ACTION')


def source_to_json(source):
    return {
        'module_id': source.module_id,
        'id': source.id,
        'group_id': source.group_id,
        'group_path_name': source.group_path_name,
        'url': source.url,
        'name': source.name,
        'thumbnail_url': source.thumbnail_url,
        'web_url': source.web_url,
        'auto_download_media': source.auto_download_media,
        'items_id': [item.id for item in source.items],
    }


def print_source(source):
    print('Module = %s' % source['module_id'])
    print('ID = %s' % source['id'])
    print('Group = %s' % source['group_path_name'])
    print('URL = %s' % source['url'])
    print('Name = %s' % source['name'])
    print('Thumbnail URL = %s' % source['thumbnail_url'])
    print('Web URL = %s' % source['web_url'])
    print('Auto Download Media = %s' % bool_to_str(source['auto_download_media']))
    print('Items = %d' % len(source['items_id']))


def print_source_table(sources):
    print(tabulate([[
        source['module_id'],
        source['id'],
        source['group_path_name'],
        source['name'],
        source['url'],
        bool_to_str(source['auto_download_media']),
    ] for source in sorted(sources, key=lambda x: (x['group_path_name'].lower(), x['name'].lower()))],
        headers=['Module', 'ID', 'Group', 'Name', 'URL', 'Auto Download']))


# Commands

parser_source_list = subparsers_source.add_parser('list',
                                                  help='lista fontes')
parser_source_list.set_defaults(_output=print_source_table)
parser_source_list.add_argument('--group', dest='group', type=read_group,
                                help='listar fontes apenas deste grupo')
parser_source_list.add_argument('--recursive', action='store_true',
                                help='listar fontes de todos os grupos a baixo do grupo informado')
parser_source_list.add_argument('--no-group', dest='group', action='store_const', const=0)


@api('GET', '/source', multiple='sources')
def source_list(group=None, recursive=None, db=None):
    if group is not None:
        group = int(group)
    if recursive is not None and isinstance(recursive, str):
        recursive = str_to_bool(recursive)
    if db is None:
        db = Session()
    if group is None:
        sources = db.query(Source).all()
    elif group == 0:
        sources = db.query(Source).filter(Source.group_id == None)
    else:
        if recursive:
            groups = get_groups_ids_recursive(db, group)
        else:
            groups = {group}
        sources = db.query(Source).filter(Source.group_id.in_(groups))
    return [source_to_json(source) for source in sources]


parser_source_show = subparsers_source.add_parser('show',
                                                  help='mostra informações da fonte')
parser_source_show.set_defaults(_output=print_source)
parser_source_show.add_argument('module',
                                help='ID do módulo')
parser_source_show.add_argument('id',
                                help='ID da fonte')


@api('GET', '/source/<module>/<id>')
def source_show(module, id, db=None):
    if db is None:
        db = Session()
    return source_to_json(get_source(db, module, id))


parser_source_add = subparsers_source.add_parser('add',
                                                 help='adiciona uma nova fonte')
parser_source_add.set_defaults(_output=print_source)
parser_source_add.add_argument('module',
                               help='ID do módulo')
parser_source_add.add_argument('url',
                               help='URL da fonte')
parser_source_add.add_argument('--id',
                               help='ID da fonte')
parser_source_add.add_argument('--group', type=read_group,
                               help='caminho do grupo')
parser_source_add.add_argument('--options',
                               help='opções do módulo para a URL')
parser_source_add.add_argument('--name',
                               help='nome da fonte')
parser_source_add.add_argument('--thumbnail',
                               help='URL da thumbnail')
parser_source_add.add_argument('--no-thumbnail', dest='thumbnail', action='store_const', const='',
                               help='cadastra sem thumbnail')
parser_source_add.add_argument('--web',
                               help='URL da página web')
parser_source_add.add_argument('--no-web', dest='web', action='store_const', const='',
                               help='cadastra sem página web')
parser_source_add.add_argument('--auto-download-media', action='store_true',
                               help='baixar novas mídias automaticamente')


@api('POST', '/source')
def source_add(module, url, id=None, group=None, options=None, name=None, thumbnail=None, web=None,
               auto_download_media=None, db=None):
    module = get_module(module)
    meta = module.get_source_metadata(url)
    if options is None:
        options = ''
    if thumbnail is None:
        thumbnail = meta.get('thumbnail_url', '')
    if web is None:
        web = meta.get('web_url', '')
    if auto_download_media is not None and isinstance(auto_download_media, str):
        auto_download_media = str_to_bool(auto_download_media)
    if db is None:
        db = Session()
    if group is not None:
        group = get_group(db, int(group)).id
    source = Source(
        module_id=module.id,
        id=id or meta['id'],
        group_id=group,
        url=url,
        name=name or meta['name'],
        thumbnail_url=thumbnail,
        web_url=web,
        auto_download_media=auto_download_media,
    )
    db.add(source)
    db.commit()
    if source.thumbnail_url:
        source.thumbnail.download()
    return source_to_json(source)


parser_source_edit = subparsers_source.add_parser('edit',
                                                  help='edita uma fonte')
parser_source_edit.set_defaults(_output=print_source)
parser_source_edit.add_argument('module',
                                help='ID do módulo')
parser_source_edit.add_argument('id',
                                help='ID da fonte')
parser_source_edit.add_argument('--group', type=read_group,
                                help='caminho do grupo')
parser_source_edit.add_argument('--no-group', dest='group', action='store_const', const=0,
                                help='remove fonte de qualquer grupo')
parser_source_edit.add_argument('--url',
                                help='URL da fonte')
parser_source_edit.add_argument('--options',
                                help='opções do módulo para a URL')
parser_source_edit.add_argument('--no-options', dest='options', action='store_const', const='',
                                help='remove opções do módulo para a URL')
parser_source_edit.add_argument('--name',
                                help='nome da fonte')
parser_source_edit.add_argument('--thumbnail',
                                help='URL da thumbnail')
parser_source_edit.add_argument('--no-thumbnail', dest='thumbnail', action='store_const', const='',
                                help='remove thumbnail')
parser_source_edit.add_argument('--web',
                                help='URL da página web')
parser_source_edit.add_argument('--no-web', dest='web', action='store_const', const='',
                                help='remove página web')
parser_source_edit.add_argument('--auto-download-media', action='store_true', default=None,
                                help='baixar novas mídias automaticamente')
parser_source_edit.add_argument('--no-auto-download_media', dest='auto_download_media', action='store_false',
                                default=None,
                                help='não baixar novas mídias automaticamente')


@api('POST', '/source/<module>/<id>')
def source_edit(module, id, group=None, url=None, options=None, name=None, thumbnail=None, web=None,
                auto_download_media=None, db=None):
    if db is None:
        db = Session()
    source = get_source(db, module, id)
    if group is not None:
        group = int(group)
        if group == 0:
            source.group_id = None
        else:
            source.group_id = get_group(group).id
    if url is not None:
        source.url = url
    if options is not None:
        source.options = options
    if name is not None:
        source.name = name
    if thumbnail is not None:
        source.thumbnail_url = thumbnail
    if web is not None:
        source.web_url = web
    if auto_download_media is not None:
        if isinstance(auto_download_media, str):
            source.auto_download_media = str_to_bool(auto_download_media)
        else:
            source.auto_download_media = auto_download_media
    db.commit()
    if thumbnail is not None:
        if thumbnail == '':
            source.thumbnail.remove()
        else:
            source.thumbnail.download()
    return source_to_json(source)


parser_source_remove = subparsers_source.add_parser('remove',
                                                    help='remove uma fonte')
parser_source_remove.add_argument('module',
                                  help='ID do módulo')
parser_source_remove.add_argument('id',
                                  help='ID da fonte')


@api('DELETE', '/source/<module>/<id>')
def source_remove(module, id, db=None):
    if db is None:
        db = Session()
    source = get_source(db, module, id)
    items = source.items
    for item in items:
        item.sources.remove(source)
        if not item.sources:
            item_remove(item.module_id, item.id, db=db)
    db.delete(source)
    db.commit()
    source.thumbnail.remove()
    return {}
