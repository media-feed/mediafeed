import os
from datetime import datetime
from sqlalchemy import (
    Column, Boolean, DateTime, ForeignKey, ForeignKeyConstraint, Integer, Sequence, String, UniqueConstraint, Table,
    Text,
)
from sqlalchemy.orm import relationship

from ..modules import get_module
from ..settings import DATA_PATH
from .errors import GroupNotFound, SourceNotFound, ItemNotFound
from .utils import Base


source_item = Table(
    'source_item',
    Base.metadata,
    Column('source_module', String(50), primary_key=True),
    Column('source_id', String(50), primary_key=True),
    Column('item_module', String(50), primary_key=True),
    Column('item_id', String(50), primary_key=True),
    ForeignKeyConstraint(('source_module', 'source_id'), ('source.module_id', 'source.id')),
    ForeignKeyConstraint(('item_module', 'item_id'), ('item.module_id', 'item.id')),
)


def get_group(db, id):
    group = db.query(Group).get(id)
    if group is None:
        raise GroupNotFound(id)
    return group


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
    name = Column(String(50), nullable=False)

    parent = relationship('Group', remote_side=id, back_populates='children')
    children = relationship('Group', remote_side=parent_id, order_by='Group.name', back_populates='parent')
    sources = relationship('Source', order_by='Source.name', back_populates='group')

    def __repr__(self):
        return '<Group "%s">' % self.path_name

    @property
    def path_ids(self):
        if self.parent_id is None:
            return [self]
        return self.parent.path_ids + [self]

    @property
    def path_name(self):
        return '/'.join(group.name for group in self.path_ids)


def get_source(db, module_id, id):
    source = db.query(Source).get((module_id, id))
    if source is None:
        raise SourceNotFound('%s:%s' % (module_id, id))
    return source


class Source(Base):
    __tablename__ = 'source'

    module_id = Column(String(50), primary_key=True)
    id = Column(String(50), primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    url = Column(String(256), nullable=False)
    options = Column(Text, nullable=False, default='')
    name = Column(String(50), nullable=False)
    thumbnail_url = Column(String(256), nullable=False, default='')
    web_url = Column(String(256), nullable=False, default='')
    auto_download_media = Column(Boolean, nullable=False, default=False)

    group = relationship('Group', back_populates='sources')
    items = relationship('Item', secondary=source_item, order_by='Item.datetime', back_populates='sources')

    def __repr__(self):
        return '<Source "%s:%s">' % (self.module_id, self.id)

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
        return Thumbnail(self, self.thumbnail_path)

    @property
    def thumbnail_path(self):
        return os.path.join(DATA_PATH, 'thumbnail', 'source', self.module_id, self.id)


def get_item(db, module_id, id):
    item = db.query(Item).get((module_id, id))
    if item is None:
        raise ItemNotFound('%s:%s' % (module_id, id))
    return item


class Item(Base):
    __tablename__ = 'item'

    module_id = Column(String(50), primary_key=True)
    id = Column(String(50), primary_key=True)
    url = Column(String(256), nullable=False)
    datetime = Column(DateTime, nullable=False)
    name = Column(String(50), nullable=False)
    thumbnail_url = Column(String(256), nullable=False, default='')
    media_url = Column(String(256), nullable=False, default='')
    text = Column(Text, nullable=False)
    viewed = Column(Boolean, nullable=False, default=False)

    sources = relationship('Source', secondary=source_item, order_by='Source.name', back_populates='items')

    def __repr__(self):
        return '<Item "%s:%s">' % (self.module_id, self.id)

    @property
    def module(self):
        return get_module(self.module_id)

    @property
    def timestamp(self):
        return self.datetime.timestamp()

    @timestamp.setter
    def timestamp(self, value):
        self.datetime = datetime.fromtimestamp(value)

    @property
    def thumbnail(self):
        return Thumbnail(self, self.thumbnail_path)

    @property
    def thumbnail_path(self):
        return os.path.join(DATA_PATH, 'thumbnail', 'source', self.module_id, self.id)

    @property
    def media_path(self):
        return os.path.join(DATA_PATH, 'media', self.module_id, self.id)


class Thumbnail(object):
    def __init__(self, model, filename):
        self.model = model
        self.module = model.module
        self.url = model.thumbnail_url
        self.path = filename

    def __repr__(self):
        return '<Thumbnail: "%s">' % self.path

    def __bool__(self):
        return self.exists()

    def exists(self):
        return os.path.exists(self.path)

    def download(self):
        self.module.get_thumbnail(self.path, self.url, self.model.options)

    def remove(self):
        if self:
            os.remove(self.path)
