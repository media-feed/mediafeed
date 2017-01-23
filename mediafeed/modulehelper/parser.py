from argparse import ArgumentParser


parser = ArgumentParser()
subparsers = parser.add_subparsers(dest='action', metavar='ACTION')


parser_info = subparsers.add_parser('info',
                                    help='mostrar informações do módulo')


parser_is_valid_url = subparsers.add_parser('is-valid-url',
                                            help='verificar se a URL é suportada pelo módulo')
parser_is_valid_url.add_argument('url', metavar='URL',
                                 help='URL da fonte')
parser_is_valid_url.add_argument('options', nargs='?',
                                 help='opções do módulo para a URL')


parser_get_source_metadata = subparsers.add_parser('get-source-metadata',
                                                   help='mostrar meta dados da fonte')
parser_get_source_metadata.add_argument('url', metavar='URL',
                                        help='URL da fonte')
parser_get_source_metadata.add_argument('options', nargs='?',
                                        help='opções do módulo para a URL')


parser_get_items = subparsers.add_parser('get-items',
                                         help='mostrar itens da fonte')
parser_get_items.add_argument('url', metavar='URL',
                              help='URL da fonte')
parser_get_items.add_argument('options', nargs='?',
                              help='opções do módulo para a URL')


parser_get_item = subparsers.add_parser('get-item',
                                        help='mostrar item')
parser_get_item.add_argument('url', metavar='URL',
                             help='URL do item')
parser_get_item.add_argument('options', nargs='?',
                             help='opções do módulo para a URL')


parser_get_thumbnail = subparsers.add_parser('get-thumbnail',
                                             help='baixar thumbnail')
parser_get_thumbnail.add_argument('filename', metavar='FILENAME',
                                  help='nome do arquivo da thumbnail')
parser_get_thumbnail.add_argument('url', metavar='URL',
                                  help='URL da thumbnail')
parser_get_thumbnail.add_argument('options', nargs='?',
                                  help='opções do módulo para a URL')


parser_get_media = subparsers.add_parser('get-media',
                                         help='baixar mídia')
parser_get_media.add_argument('dirname', metavar='DIRNAME',
                              help='diretório para salvar a mídia')
parser_get_media.add_argument('url', metavar='URL',
                              help='URL da mídia')
parser_get_media.add_argument('options', nargs='?',
                              help='opções do módulo para a URL')
