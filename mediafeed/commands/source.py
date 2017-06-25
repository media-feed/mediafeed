from datetime import datetime
from logging import getLogger

from ..databases import Item
from ..databases import Source, get_source
from ..databases import get_group, get_groups_ids_recursive
from ..modules import get_module
from .item import add_item
from .utils import with_db


__all__ = ('list_sources', 'show_source', 'add_source', 'edit_source', 'remove_source', 'update_items')


logger = getLogger('mediafeed.commands.source')


@with_db
def list_sources(group_id=0, recursive=None, auto_download_media=None, persist_thumbnails=None, error=None, db=None):
    logger.debug('list_sources group_id=%r recursive=%r auto_download_media=%r persist_thumbnails=%r error=%r' % (
        group_id, recursive, auto_download_media, persist_thumbnails, error))
    if group_id == 0 or group_id is None and recursive:
        sources = db.query(Source).all()
    elif group_id is None:
        sources = db.query(Source).filter(Source.group_id == None)
    else:
        if recursive:
            groups = get_groups_ids_recursive(group_id)
        else:
            groups = {group_id}
        sources = db.query(Source).filter(Source.group_id.in_(groups))
    if auto_download_media is not None:
        sources = sources.filter(Source.auto_download_media == auto_download_media)
    if persist_thumbnails is not None:
        sources = sources.filter(Source.persist_thumbnails == persist_thumbnails)
    if error is not None:
        if error:
            sources = sources.filter(Source.error != None)
        else:
            sources = sources.filter(Source.error == None)
    return [source.to_dict() for source in sources]


@with_db
def show_source(module_id, id, db=None):
    logger.debug('show_source module_id=%r id=%r' % (module_id, id))
    source = get_source(db, module_id, id)
    return source.to_dict()


@with_db
def add_source(module_id, url, id=None, group_id=None, options=None, name=None, thumbnail_url=None, web_url=None,
               auto_download_media=None, persist_thumbnails=None, db=None):
    logger.debug('add_source module_id=%r url=%r' % (module_id, url))
    module = get_module(module_id)
    meta = module.get_source_metadata(url, options)
    if group_id is not None:
        group = get_group(db, group_id)
    else:
        group = None
    source = Source(
        module_id=module.id,
        id=id or meta['id'],
        group=group,
        url=url,
        options=options,
        name=name or meta['name'],
        thumbnail_url=thumbnail_url if thumbnail_url is not None else meta.get('thumbnail_url'),
        web_url=web_url if web_url is not None else meta.get('web_url'),
        auto_download_media=auto_download_media,
        persist_thumbnails=persist_thumbnails,
    )
    db.add(source)
    db.commit()
    if source.thumbnail:
        source.thumbnail.download()
    return source.to_dict()


@with_db
def edit_source(module_id, id, group_id=0, url=None, options=None, name=None, thumbnail_url=None, web_url=None,
                auto_download_media=None, persist_thumbnails=None, db=None):
    logger.debug('edit_source module_id=%r id=%r' % (module_id, id))
    source = get_source(db, module_id, id)
    if group_id is None:
        source.group_id = None
    elif group_id:
        group = get_group(db, group_id)
        source.group = group
    if url is not None:
        source.url = url
    if options is not None:
        source.options = options
    if name is not None:
        source.name = name
    if thumbnail_url is not None:
        source.thumbnail_url = thumbnail_url
    if web_url is not None:
        source.web_url = web_url
    if auto_download_media is not None:
        source.auto_download_media = auto_download_media
    if persist_thumbnails is not None:
        source.persist_thumbnails = persist_thumbnails
    db.commit()
    if thumbnail_url is not None:
        if thumbnail_url == '':
            del source.thumbnail
        else:
            source.thumbnail.download()
    return source.to_dict()


@with_db
def remove_source(module_id, id, db=None):
    logger.debug('remove_source module_id=%r id=%r' % (module_id, id))
    source = get_source(db, module_id, id)
    db.delete(source)
    db.commit()
    del source.thumbnail
    return {}


@with_db
def update_items(module_id, id, viewed=None, db=None):
    logger.debug('check_new_items module_id=%r id=%r' % (module_id, id))
    module = get_module(module_id)
    source = get_source(db, module_id, id)
    logger.info('Verificando novos itens de "%s"' % source.name)
    items_id = {item.id for item in source.items}
    try:
        for item_data in module.get_items(source.url, source.options):
            if item_data['id'] in items_id:
                continue
            item = db.query(Item).get((module_id, item_data['id']))
            if item is not None:
                logger.debug('%r: append %r' % (source, item))
                logger.info('%s: atribuindo -> %s' % (source.name, item.name))
                source.items.append(item)
                db.commit()
            else:
                logger.debug('%r: criando item %r' % (source, item_data['id']))
                if 'name' not in item_data:
                    item_data = module.get_item(item_data['url'], source.options)
                logger.info('%s: novo item -> %s' % (source.name, item_data['name']))
                add_item(module_id, source.id, viewed=viewed, **item_data, db=db)
        source.error = ''
        source.last_success_update = datetime.now()
    except Exception as e:
        source.error = str(e)
    db.commit()
    return source.to_dict()
