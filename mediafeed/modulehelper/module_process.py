import os

from .errors import ActionNotImplemented
from .parser import parser
from .utils import download, print_json, print_jsons


class ModuleProcess(object):
    def __call__(self, args=None):
        if args is None:
            args = parser.parse_args()

        if args.action == 'info':
            print_json(self.info())
            return 0

        if args.action == 'is-valid-url':
            if self.is_valid_url(args.url, args.options):
                return 0
            return 1

        if args.action == 'get-source-metadata':
            print_json(self.get_source_metadata(args.url, args.options))
            return 0

        if args.action == 'get-items':
            print_jsons(self.get_items(args.url, args.options))
            return 0

        if args.action == 'get-item':
            print_json(self.get_item(args.url, args.options))
            return 0

        if args.action == 'get-thumbnail':
            self.get_thumbnail(args.filename, args.url, args.options)
            return 0

        if args.action == 'get-media':
            self.get_media(args.dirname, args.url, args.options)
            return 0

        parser.print_usage()
        return 2

    def info(self):
        raise ActionNotImplemented('info')

    def is_valid_url(self, url, options=None):
        raise ActionNotImplemented('is_valid_url')

    def get_source_metadata(self, url, options=None):
        raise ActionNotImplemented('get_source_metadata')

    def get_items(self, url, options=None):
        raise ActionNotImplemented('get_items')

    def get_item(self, url, options=None):
        raise ActionNotImplemented('get_item')

    def get_thumbnail(self, filename, url, options=None):
        download(filename, url)

    def get_media(self, dirname, url, options=None):
        download(os.path.join(dirname, 'file'), url)
