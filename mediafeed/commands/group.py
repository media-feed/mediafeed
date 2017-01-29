import os

from ..cli.parser import subparsers
from ..databases import Group, Session, get_group
from .api import api
from .errors import CommandError


__all__ = ('parser_group', 'group_list', 'group_show', 'group_add', 'group_edit', 'group_remove')


parser_group = subparsers.add_parser('group',
                                     help='comandos de grupos')
subparsers_group = parser_group.add_subparsers(dest='_action', metavar='ACTION')


def group_to_json(group, recursive=False):
    children = [(child.id, child.name) for child in group.children]
    sources = [(source.id, source.name) for source in group.sources]
    json = {
        'id': group.id,
        'parent_id': group.parent_id,
        'parent_path_name': group.parent.path_name if group.parent else '',
        'name': group.name,
        'path_name': group.path_name,
        'children_id': [id for id, _ in children],
        'children_names': [name for _, name in children],
        'sources_id': [id for id, _ in sources],
        'sources_names': [name for _, name in sources],
    }
    if recursive:
        json['children'] = [group_to_json(child, recursive=recursive) for child in group.children]
    return json


def print_group(group):
    print('ID = %s' % group['id'])
    print('Parent = %s' % group['parent_path_name'])
    print('Name = %s' % group['name'])
    print('Children = %s' % ', '.join(sorted(group['children_names'], key=lambda x: x.lower())))
    print('Sources = %s' % ', '.join(sorted(group['sources_names'], key=lambda x: x.lower())))


def print_group_tree(groups):
    def make_tree(groups):
        lines = []
        for group in sorted(groups, key=lambda x: x['name'].lower()):
            lines.append('- %s' % group['name'])
            for source in sorted(group['sources_names'], key=lambda x: x.lower()):
                lines.append('  * %s' % source)
            lines += ['  ' + line for line in make_tree(group['children'])]
        return lines
    print(os.linesep.join(make_tree(groups)))


def read_group(arg):
    path = arg.split('/')
    db = Session()
    group = db.query(Group.id).filter(Group.parent_id == None, Group.name == path[0]).first()[0]
    for i in range(1, len(path)):
        group = db.query(Group.id).filter(Group.parent_id == group, Group.name == path[i]).first()[0]
    return group


# Commands

parser_group_list = subparsers_group.add_parser('list',
                                                help='mostra a árvore de grupos')
parser_group_list.set_defaults(_output=print_group_tree)
parser_group_list.add_argument('-r', '--root', metavar='GROUP', type=read_group,
                               help='mostra a árvore a baixo deste grupo')


@api('GET', '/group', multiple='groups')
def group_list(root=None, db=None):
    if root is not None:
        root = int(root)
    if db is None:
        db = Session()
    if root is None:
        groups = db.query(Group).filter(Group.parent_id == None).all()
    else:
        groups = db.query(Group).filter(Group.id == root).all()
    return [group_to_json(group, recursive=True) for group in groups]


parser_group_show = subparsers_group.add_parser('show',
                                                help='mostra informações do grupo')
parser_group_show.set_defaults(_output=print_group)
parser_group_show.add_argument('id', type=read_group,
                               help='caminho do grupo')


@api('GET', '/group/<id>')
def group_show(id, db=None):
    id = int(id)
    if db is None:
        db = Session()
    return group_to_json(get_group(db, id))


parser_group_add = subparsers_group.add_parser('add',
                                               help='adiciona um novo grupo')
parser_group_add.set_defaults(_output=print_group)
parser_group_add.add_argument('name',
                              help='nome do grupo')
parser_group_add.add_argument('--parent', type=read_group,
                              help='grupo pai')


@api('POST', '/group')
def group_add(name, parent=None, db=None):
    if parent is not None:
        parent = int(parent)
    if db is None:
        db = Session()
    group = Group(
        parent_id=parent,
        name=name,
    )
    db.add(group)
    db.commit()
    return group_to_json(group)


parser_group_edit = subparsers_group.add_parser('edit',
                                                help='edita um grupo')
parser_group_edit.set_defaults(_output=print_group)
parser_group_edit.add_argument('id', type=read_group,
                               help='caminho do grupo')
parser_group_edit.add_argument('--parent', type=read_group, default=None,
                               help='pai do grupo')
parser_group_edit.add_argument('--no-parent', dest='parent', action='store_const', const=0, default=None,
                               help='define o grupo na raíz da árvore de grupos')
parser_group_edit.add_argument('--name',
                               help='nome do grupo')


@api('POST', '/group/<id>')
def group_edit(id, parent=None, name=None, db=None):
    id = int(id)
    if parent is not None:
        parent = int(parent)
    if db is None:
        db = Session()
    group = get_group(db, id)
    if parent == 0:
        group.parent_id = None
    elif parent:
        p = get_group(db, parent)
        while p:
            if p.id == id:
                raise CommandError('Loop na árvore de grupos')
            p = p.parent
        group.parent_id = parent
    if name:
        group.name = name
    db.commit()
    return group_to_json(group)


parser_group_remove = subparsers_group.add_parser('remove',
                                                  help='remove um grupo')
parser_group_remove.add_argument('id', type=read_group,
                                 help='caminho do grupo')


@api('DELETE', '/group/<id>')
def group_remove(id, db=None):
    id = int(id)
    if db is None:
        db = Session()
    group = get_group(db, id)
    db.delete(group)
    db.commit()
    return {}
