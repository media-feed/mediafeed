from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Sequence, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..modules import get_module
from .errors import GroupNotFound, SourceNotFound
from .utils import Base


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
