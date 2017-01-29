from sqlalchemy import Column, ForeignKey, Integer, Sequence, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .errors import GroupNotFound
from .utils import Base


def get_group(db, id):
    group = db.query(Group).get(id)
    if group is None:
        raise GroupNotFound(id)
    return group


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
