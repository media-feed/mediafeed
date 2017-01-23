import os
from json import loads
from logging import getLogger
from subprocess import DEVNULL, PIPE, Popen
from traceback import format_exc

from .errors import ModuleProcessError, ModuleProcessExitError


logger = getLogger('mediafeed.modules')


class Module(object):
    def __init__(self, id, path):
        self.id = id
        self.path = path
        self._load_info()

    def __repr__(self):
        return '<Module "%s">' % self.id

    def _exec(self, args):
        cmd = [self.path] + args
        logger.debug('Executando %s' % cmd)
        with Popen(cmd, stdout=DEVNULL) as p:
            exit = p.wait()
            if exit:
                raise ModuleProcessExitError(exit)

    def _exec_json(self, args):
        cmd = [self.path] + args
        logger.debug('Executando %s' % cmd)
        with Popen(cmd, stdout=PIPE) as p:
            stdout = p.stdout.read()

            exit = p.wait()
            if exit:
                raise ModuleProcessExitError(exit)

            return loads(stdout.decode())

    def _exec_jsons(self, args):
        cmd = [self.path] + args
        logger.debug('Executando %s' % cmd)
        with Popen(cmd, stdout=PIPE) as p:
            for line in p.stdout:
                yield loads(line.decode())

            exit = p.wait()
            if exit:
                raise ModuleProcessExitError(exit)

    def _load_info(self):
        try:
            info = self._exec_json(['info'])
            self.name = info['name']
            self.media = info['media']
            self.description = info.get('description', '')
            self.options = info.get('options', '')
        except Exception as e:
            raise ModuleProcessError(self.id, 'info') from e

    def is_valid_url(self, url, options=None):
        cmd = ['is-valid-url', url]
        if options is not None:
            cmd.append(options)
        try:
            try:
                self._exec(cmd)
                return True
            except ModuleProcessExitError as e:
                if e.exit_status == 1:
                    return False
                raise
        except Exception as e:
            e = ModuleProcessError(self.id, 'is-valid-url', url, options)
            logger.error(e)
            logger.debug(format_exc())
            return False

    def get_source_metadata(self, url, options=None):
        cmd = ['get-source-metadata', url]
        if options is not None:
            cmd.append(options)
        try:
            return self._exec_json(cmd)
        except Exception as e:
            raise ModuleProcessError(self.id, 'get-source-metadata', url, options) from e

    def get_items(self, url, options=None):
        cmd = ['get-items', url]
        if options is not None:
            cmd.append(options)
        try:
            yield from self._exec_jsons(cmd)
        except Exception as e:
            raise ModuleProcessError(self.id, 'get-items', url, options) from e

    def get_item(self, url, options=None):
        cmd = ['get-item', url]
        if options is not None:
            cmd.append(options)
        try:
            return self._exec_json(cmd)
        except Exception as e:
            raise ModuleProcessError(self.id, 'get-item', url, options) from e

    def get_thumbnail(self, filename, url, options=None):
        cmd = ['get-thumbnail', filename, url]
        if options is not None:
            cmd.append(options)
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self._exec(cmd)
        except Exception as e:
            raise ModuleProcessError(self.id, 'get-thumbnail', url, options) from e

    def get_media(self, dirname, url, options=None):
        cmd = ['get-media', dirname, url]
        if options is not None:
            cmd.append(options)
        try:
            os.makedirs(dirname, exist_ok=True)
            self._exec(cmd)
        except Exception as e:
            raise ModuleProcessError(self.id, 'get-media', url, options) from e
