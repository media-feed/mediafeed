from argparse import ArgumentParser
from logging import DEBUG, INFO, WARNING


from .. import __version__


parser = ArgumentParser()
parser.add_argument('--version', action='version', version='%(prog)s v' + __version__,
                    help='mostra número de versão e finaliza programa')
parser.add_argument('-v', '--verbose', dest='_loglevel', action='store_const', const=INFO, default=WARNING,
                    help='habilita logs do sistema')
parser.add_argument('--debug', dest='_loglevel', action='store_const', const=DEBUG, default=WARNING,
                    help='habilita logs de debug')
subparsers = parser.add_subparsers(dest='_option', metavar='OPTION')
