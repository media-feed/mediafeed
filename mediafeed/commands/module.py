from tabulate import tabulate

from ..cli.parser import subparsers
from ..modules import get_module, get_modules
from .api import api


__all__ = ('parser_module', 'module_list', 'module_show', 'module_source')


parser_module = subparsers.add_parser('module',
                                      help='comandos de módulos de fontes')
subparsers_module = parser_module.add_subparsers(dest='_action', metavar='ACTION')


def module_to_json(module):
    return {
        'id': module.id,
        'name': module.name,
        'media': module.media,
        'description': module.description,
        'options': module.options,
    }


def print_module(module):
    print('ID = %s' % module['id'])
    print('Name = %s' % module['name'])
    print('Media = %s' % module['media'])
    print('Description = %s' % module['description'])
    print('Options = %s' % module['options'])


def print_module_table(modules):
    print(tabulate([[
        module['id'],
        module['name'],
        module['media'],
        module['description'],
    ] for module in sorted(modules, key=lambda x: x['name'].lower())],
        headers=['ID', 'Name', 'Media', 'Description']))


def print_source_metadata(metadata):
    print('ID = %s' % metadata['id'])
    print('URL = %s' % metadata['url'])
    print('Options = %s' % metadata.get('options', ''))
    print('Name = %s' % metadata['name'])
    print('Thumbnail URL = %s' % metadata.get('thumbnail_url', ''))
    print('Web URL = %s' % metadata.get('web_url', ''))


# Commands

parser_module_list = subparsers_module.add_parser('list',
                                                  help='lista módulos de fontes')
parser_module_list.set_defaults(_output=print_module_table)
parser_module_list.add_argument('--url',
                                help='mostra apenas os módulos que suportam esta URL')
parser_module_list.add_argument('--options',
                                help='opções do módulo para a URL')


@api('GET', '/module', multiple='modules')
def module_list(url=None, options=None):
    return [module_to_json(module) for module in get_modules(url, options)]


parser_module_show = subparsers_module.add_parser('show',
                                                  help='mostrar informações do módulo')
parser_module_show.set_defaults(_output=print_module)
parser_module_show.add_argument('id',
                                help='ID do módulo')


@api('GET', '/module/<id>')
def module_show(id):
    return module_to_json(get_module(id))


parser_module_source = subparsers_module.add_parser('source',
                                                    help='mostra meta dados da fonte')
parser_module_source.set_defaults(_output=print_source_metadata)
parser_module_source.add_argument('id',
                                  help='ID do módulo')
parser_module_source.add_argument('url',
                                  help='URL da fonte')
parser_module_source.add_argument('options', nargs='?',
                                  help='opções do módulo para a URL')


@api('GET', '/module/<id>/source/<url:path>')
def module_source(id, url, options=None):
    module = get_module(id)
    return module.get_source_metadata(url, options)
