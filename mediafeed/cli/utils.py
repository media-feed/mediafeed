from logging import basicConfig, getLogger
from traceback import format_exc

from .. import commands, init
from .parser import parser


logger = getLogger('mediafeed.cli')


def main(args=None):
    try:
        if args is None:
            args = parser.parse_args()
        kwargs = {key: value for key, value in args.__dict__.items() if not key.startswith('_')}

        basicConfig(
            level=args._loglevel,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%H:%M:%S',
        )

        init()

        if args._option:
            if args._action:
                command = getattr(commands, '%s_%s' % (args._option, args._action))
                ret = command(**kwargs)
                if hasattr(args, '_output'):
                    args._output(ret)
                return 0

            getattr(commands, 'parser_%s' % args._option).print_usage()
            return 2

        parser.print_usage()
        return 2
    except Exception as e:
        logger.error(e)
        logger.debug(format_exc())
        return 1
