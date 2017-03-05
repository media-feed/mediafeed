import os
from json import loads
from logging import getLogger
from subprocess import DEVNULL, PIPE, Popen

from .errors import ModuleProcessError, ModuleProcessStatusError


logger = getLogger('mediafeed.modules')


class Module(object):
    def __init__(self, id, path):
        self.id = id
        self.path = path
        self._load_info()

    def __repr__(self):
        return '<Module "%s">' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'media': self.media,
            'description': self.description,
            'options': self.options,
        }

    def _get_exec(self, args, options=None, stdout=DEVNULL):
        cmd = [self.path] + args
        if options:
            cmd.append(options)
        logger.debug('Executando %r' % cmd)
        return Popen(cmd, stdout=stdout)

    def _exec(self, args, options=None):
        with self._get_exec(args, options=options) as p:
            status = p.wait()
            if status:
                raise ModuleProcessStatusError(status)

    def _exec_status(self, args, options=None):
        with self._get_exec(args, options=options) as p:
            status = p.wait()
            if status == 0:
                return True
            if status == 1:
                return False
            raise ModuleProcessStatusError(status)

    def _exec_json(self, args, options=None):
        with self._get_exec(args, options=options, stdout=PIPE) as p:
            stdout = p.stdout.read()

            status = p.wait()
            if status:
                raise ModuleProcessStatusError(status)

            return loads(stdout.decode())

    def _exec_jsons(self, args, options=None):
        with self._get_exec(args, options=options, stdout=PIPE) as p:
            for line in p.stdout:
                yield loads(line.decode())

            status = p.wait()
            if status:
                raise ModuleProcessStatusError(status)

    def _load_info(self):
        try:
            info = self._exec_json(['info'])
            self.name = info.get('name', self.id)
            self.media = info['media']
            self.description = info.get('description', '')
            self.options = info.get('options', '')
        except Exception as e:
            raise ModuleProcessError(self, 'info') from e

    def is_valid_url(self, url, options=None):
        try:
            cmd = ['is-valid-url', '--', url]
            return self._exec_status(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'is-valid-url', url, options) from e

    def get_source_metadata(self, url, options=None):
        try:
            cmd = ['get-source-metadata', '--', url]
            return self._exec_json(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'get-source-metadata', url, options) from e

    def get_items(self, url, options=None):
        try:
            cmd = ['get-items', '--', url]
            yield from self._exec_jsons(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'get-items', url, options) from e

    def get_item(self, url, options=None):
        try:
            cmd = ['get-item', '--', url]
            return self._exec_json(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'get-item', url, options) from e

    def get_thumbnail(self, filename, url, options=None):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            cmd = ['get-thumbnail', '--', filename, url]
            self._exec(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'get-thumbnail', url, options) from e

    def get_media(self, dirname, url, options=None):
        try:
            os.makedirs(dirname, exist_ok=True)
            cmd = ['get-media', '--', dirname, url]
            self._exec(cmd, options)
        except Exception as e:
            raise ModuleProcessError(self, 'get-media', url, options) from e
