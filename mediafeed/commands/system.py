from sqlalchemy import and_, or_

from ..cli.parser import subparsers
from ..commands import get_app
from ..databases import Session, Source, Item, get_group, get_groups_ids_recursive
from ..settings import DAEMON_PORT
from .utils import str_to_bool, read_group, read_source


__all__ = ('parser_system', 'system_daemon', 'system_update')


parser_system = subparsers.add_parser('system',
                                      help='comandos do sistema')
subparsers_system = parser_system.add_subparsers(dest='_action', metavar='ACTION')


parser_system_start = subparsers_system.add_parser('daemon',
                                                   help='iniciar daemon')


def system_daemon():
    get_app().run(port=DAEMON_PORT)


parser_system_update = subparsers_system.add_parser('update',
                                                    help='atualiza fontes')
parser_system_update.add_argument('--group', dest='groups', action='append', type=read_group,
                                  help='atualiza fontes apenas deste grupo')
parser_system_update.add_argument('--recursive', action='store_true',
                                  help='')
parser_system_update.add_argument('--source', dest='sources', action='append', type=read_source,
                                  help='')
parser_system_update.add_argument('--viewed', action='store_true')


def system_update(groups=None, recursive=None, sources=None, viewed=None, db=None):
    if recursive is not None and isinstance(recursive, str):
        recursive = str_to_bool(recursive)
    if viewed is not None and isinstance(viewed, str):
        viewed = str_to_bool(viewed)
    if db is None:
        db = Session()
    if groups is None:
        groups = []
    if recursive:
        groups = {g for group in groups for g in get_groups_ids_recursive(db, group)}
    sources_ids = sources or []
    for group in groups:
        sources_ids += [(source.module_id, source.id) for source in get_group(db, group).sources]
    sources = db.query(Source)
    if sources_ids:
        sources = sources.filter(or_(and_(Source.module_id == source[0], Source.id == source[1])
                                     for source in sources_ids))
    for source in sources.all():
        module = source.module
        items_data = list(module.get_items(source.url))
        for n, item_data in enumerate(items_data, start=1):
            item = db.query(Item).get((module.id, item_data['id']))
            if not item:
                if 'name' not in item_data:
                    item_data = module.get_item(item_data['url'])
                item = Item(
                    module_id=module.id,
                    id=item_data['id'],
                    url=item_data['url'],
                    timestamp=item_data['date'],
                    name=item_data['name'],
                    thumbnail_url=item_data.get('thumbnail_url', ''),
                    media_url=item_data.get('media_url', ''),
                    text=item_data.get('text', ''),
                    viewed=viewed,
                )
                db.add(item)
                if item.thumbnail_url:
                    module.get_thumbnail(item.thumbnail_path, item.thumbnail_url)
                if not viewed and source.auto_download_media:
                    module.get_media(item.media_path, item.url)
            if source not in item.sources:
                item.sources.append(source)
            db.commit()
