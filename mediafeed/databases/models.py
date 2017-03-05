from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Sequence, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from urllib.parse import quote

from ..modules import get_module
from .errors import GroupNotFound, ItemNotFound, SourceNotFound
from .files import Thumbnail, get_media_path, get_medias, remove_medias
from .utils import Base


source_item = Table(
    'source_item',
    Base.metadata,
    Column('source_module', String(64), primary_key=True),
    Column('source_id', String(64), primary_key=True),
    Column('item_module', String(64), primary_key=True),
    Column('item_id', String(64), primary_key=True),
    ForeignKeyConstraint(('source_module', 'source_id'), ('source.module_id', 'source.id')),
    ForeignKeyConstraint(('item_module', 'item_id'), ('item.module_id', 'item.id')),
)


def get_group(db, id):
    group = db.query(Group).get(id)
    if group is None:
        raise GroupNotFound(id)
    return group


def get_groups_root(db):
    return db.query(Group).filter(Group.parent_id == None).order_by(Group.name).all()


def get_groups_ids_recursive(db, id):
    def aux(group):
        groups.add(group.id)
        for child in group.children:
            aux(child)
    groups = set()
    aux(get_group(db, id))
    return groups


class Group(Base):
    __tablename__ = 'group'
    __table_args__ = (
        UniqueConstraint('parent_id', 'name'),
    )

    id = Column(Integer, Sequence('group_id_seq'), primary_key=True)
    parent_id = Column(Integer, ForeignKey('group.id'))
    name = Column(String(64), nullable=False)

    parent = relationship('Group', remote_side=id, back_populates='children')
    children = relationship('Group', remote_side=parent_id, order_by='Group.name', back_populates='parent')
    sources = relationship('Source', order_by='Source.name', back_populates='group')

    def __repr__(self):
        return '<Group "%s">' % self.path_name

    def to_dict(self, recursive=False):
        d = {
            'id': self.id,
            'parent_id': self.parent_id,
            'parent_path_name': self.parent.path_name if self.parent else '',
            'name': self.name,
            'path_name': self.path_name,
            'children_id': [child.id for child in self.children],
            'sources_id': [source.id for source in self.sources],
        }
        if recursive:
            d['children'] = [child.to_dict(recursive=recursive) for child in self.children]
        return d

    @property
    def path(self):
        if self.parent_id is None:
            return [self]
        return self.parent.path + [self]

    @property
    def path_name(self):
        return '/'.join(group.name for group in self.path)


def get_source(db, module_id, id):
    source = db.query(Source).get((module_id, id))
    if source is None:
        raise SourceNotFound('%s:%s' % (module_id, id))
    return source


class Source(Base):
    __tablename__ = 'source'

    module_id = Column(String(64), primary_key=True)
    id = Column(String(64), primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    url = Column(String(256), nullable=False)
    options = Column(Text, nullable=False, default='')
    name = Column(String(64), nullable=False)
    thumbnail_url = Column(String(256), nullable=False, default='')
    web_url = Column(String(256), nullable=False, default='')
    auto_download_media = Column(Boolean, nullable=False, default=False)
    persist_thumbnails = Column(Boolean, nullable=False, default=False)
    last_success_update = Column(DateTime)
    error = Column(Text)

    group = relationship('Group', back_populates='sources')
    items = relationship('Item', secondary=source_item, order_by='Item.datetime', back_populates='sources')

    def __repr__(self):
        return '<Source "%s:%s">' % (self.module_id, self.id)

    def to_dict(self):
        last_success = self.last_success_update
        return {
            'module_id': self.module_id,
            'id': self.id,
            'group_id': self.group_id,
            'group_path_name': self.group_path_name,
            'url': self.url,
            'options': self.options,
            'name': self.name,
            'thumbnail_url': self.thumbnail.path,
            'web_url': self.web_url,
            'auto_download_media': self.auto_download_media,
            'persist_thumbnails': self.persist_thumbnails,
            'last_success_update': str(last_success) if last_success else None,
            'last_success_update_timestamp': last_success.timestamp() if last_success else None,
            'error': self.error,
            'items_id': [item.id for item in self.items],
        }

    @property
    def module(self):
        return get_module(self.module_id)

    @property
    def group_path_name(self):
        if self.group:
            return self.group.path_name
        return ''

    @property
    def thumbnail(self):
        return Thumbnail(self)

    @thumbnail.deleter
    def thumbnail(self):
        self.thumbnail.remove()


def get_item(db, module_id, id):
    item = db.query(Item).get((module_id, id))
    if item is None:
        raise ItemNotFound('%s:%s' % (module_id, id))
    return item


class Item(Base):
    __tablename__ = 'item'

    module_id = Column(String(64), primary_key=True)
    id = Column(String(64), primary_key=True)
    url = Column(String(256), nullable=False)
    datetime = Column(DateTime, nullable=False)
    name = Column(String(64), nullable=False)
    thumbnail_url = Column(String(256), nullable=False, default='')
    media_url = Column(String(256), nullable=False, default='')
    viewed = Column(Boolean, nullable=False, default=False)
    text = Column(Text, nullable=False)

    sources = relationship('Source', secondary=source_item, order_by='Source.name', back_populates='items')

    def __repr__(self):
        return '<Item "%s:%s">' % (self.module_id, self.id)

    def to_dict(self):
        return {
            'module_id': self.module.id,
            'id': self.id,
            'sources_id': [source.id for source in self.sources],
            'url': self.url,
            'datetime': str(self.datetime),
            'timestamp': self.timestamp,
            'name': self.name,
            'thumbnail_url': self.thumbnail.path,
            'media_url': self.media_url,
            'viewed': self.viewed,
            'text': self.text,
            'medias': [quote(media.filename) for media in self.medias],
        }

    @property
    def module(self):
        return get_module(self.module_id)

    @property
    def options(self):
        if self.sources:
            return self.sources[0].options

    @property
    def timestamp(self):
        return self.datetime.timestamp()

    @timestamp.setter
    def timestamp(self, value):
        self.datetime = datetime.fromtimestamp(value)

    @property
    def thumbnail(self):
        return Thumbnail(self)

    @thumbnail.deleter
    def thumbnail(self):
        self.thumbnail.remove()

    @property
    def media_path(self):
        return get_media_path(self)

    @property
    def medias(self):
        return get_medias(self)

    @medias.deleter
    def medias(self):
        remove_medias(self)
