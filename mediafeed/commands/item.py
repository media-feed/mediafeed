from logging import getLogger
from sqlalchemy import and_, or_

from ..databases import Item, get_item
from ..databases import Source, get_source
from ..databases import get_group, get_groups_ids_recursive
from .utils import with_db


__all__ = ('list_items', 'show_item', 'add_item', 'edit_item', 'remove_item', 'download_media', 'remove_media')


logger = getLogger('mediafeed.commands.item')


@with_db
def list_items(groups_id=None, recursive=False, sources_id=None, viewed=None, media=None, db=None):
    logger.debug('list_items groups_id=%r recursive=%r sources_id=%r viewed=%r media=%r' % (
        groups_id, recursive, sources_id, viewed, media))
    if groups_id is None:
        groups_id = set()
    if recursive:
        groups_id = {id for group_id in groups_id for id in get_groups_ids_recursive(db, group_id)}
    if sources_id is None:
        sources_id = set()
    sources_id = sources_id.union({(source.module_id, source.id)
                                   for group_id in groups_id
                                   for source in get_group(db, group_id).sources})
    if groups_id and not sources_id:
        return []
    items = db.query(Item)
    if viewed is not None:
        items = items.filter(Item.viewed == viewed)
    if sources_id:
        items = items.join(Source.items).filter(or_(and_(Source.module_id == source_id[0], Source.id == source_id[1])
                                                    for source_id in sources_id))
    items = items.all()
    if media is not None:
        items = [item for item in items if bool(item.medias) == media]
    return [item.to_dict() for item in items]


@with_db
def show_item(module_id, id, db=None):
    logger.debug('show_item module_id=%r id=%r' % (module_id, id))
    item = get_item(db, module_id, id)
    return item.to_dict()


@with_db
def add_item(module_id, source_id, id, url, timestamp, name, text, thumbnail_url=None, media_url=None, viewed=None,
             db=None):
    logger.debug('add_item module_id=%r source_id=%r id=%r url=%r' % (module_id, source_id, id, url))
    source = get_source(db, module_id, source_id)
    item = db.query(Item).get((module_id, id))
    if not item:
        item = Item(
            module_id=module_id,
            id=id,
            url=url,
            timestamp=timestamp,
            name=name,
            thumbnail_url=thumbnail_url,
            media_url=media_url,
            viewed=viewed,
            text=text,
        )
        db.add(item)
    source.items.append(item)
    db.commit()
    if source.persist_thumbnails:
        item.thumbnail.download(source.options)
    if source.auto_download_media:
        download_media(module_id, id, source.options, db=db)
    return item.to_dict()


@with_db
def edit_item(module_id, id, url=None, timestamp=None, name=None, thumbnail_url=None, media_url=None, viewed=None,
              text=None, db=None):
    logger.debug('edit_item module_id=%r id=%r' % (module_id, id))
    item = get_item(db, module_id, id)
    if url is not None:
        item.url = url
    if timestamp is not None:
        item.timestamp = timestamp
    if name is not None:
        item.name = name
    if thumbnail_url is not None:
        item.thumbnail_url = thumbnail_url
    if media_url is not None:
        item.media_url = media_url
    if viewed is not None:
        item.viewed = viewed
    if text is not None:
        item.text = text
    db.commit()
    if thumbnail_url is not None and item.thumbnail.local_path:
        item.thumbnail.download()
    return item.to_dict()


@with_db
def remove_item(module_id, id, db=None):
    logger.debug('remove_item module_id=%r id=%r' % (module_id, id))
    item = get_item(db, module_id, id)
    db.delete(item)
    db.commit()
    del item.thumbnail
    del item.medias
    return {}


@with_db
def download_media(module_id, item_id, options=None, db=None):
    logger.debug('download_media module_id=%r item_id=%r options=%r' % (module_id, item_id, options))
    item = get_item(db, module_id, item_id)
    module = item.module
    thumbnail = item.thumbnail
    if item.media_url:
        if options is None:
            options = item.sources[0].options
        if not thumbnail.local_path:
            thumbnail.download(options)
        module.get_media(item.media_path, item.media_url, options)
    else:
        logger.debug('download_media module_id=%r item_id=%r não possui URL de mídia')
    return item.to_dict()


@with_db
def remove_media(module_id, item_id, filename=None, db=None):
    logger.debug('remove_media module_id=%r item_id=%r filename=%r' % (module_id, item_id, filename))
    item = get_item(db, module_id, item_id)
    if filename is None:
        del item.medias
    else:
        for media in item.medias:
            if media.filename == filename or media.media_filename == filename:
                media.remove()
    if not any(source.persist_thumbnails for source in item.sources):
        del item.thumbnail
    return item.to_dict()
