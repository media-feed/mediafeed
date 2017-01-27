from ..cli.parser import subparsers
from ..commands import get_app
from ..settings import DAEMON_PORT


__all__ = ('parser_system', 'system_daemon')


parser_system = subparsers.add_parser('system',
                                      help='comandos do sistema')
subparsers_system = parser_system.add_subparsers(dest='_action', metavar='ACTION')


parser_system_start = subparsers_system.add_parser('daemon',
                                                   help='iniciar daemon')


def system_daemon():
    get_app().run(port=DAEMON_PORT)
