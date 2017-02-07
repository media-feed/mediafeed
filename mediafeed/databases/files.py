import os
from shutil import rmtree

from ..settings import DATA_PATH


class Thumbnail(object):
    def __init__(self, model):
        self.model = model
        self.module = model.module
        self.filename = os.path.join('thumbnails', model.__tablename__, self.module.id, model.id)
        self.full_filename = os.path.join(DATA_PATH, self.filename)
        self.url = model.thumbnail_url

    def __repr__(self):
        return '<Thumbnail "%s">' % self.filename

    def __bool__(self):
        return bool(self.path)

    @property
    def path(self):
        if self.local_path:
            return self.filename
        if self.online_path:
            return self.online_path
        return ''

    @property
    def local_path(self):
        if os.path.exists(self.full_filename):
            return self.full_filename

    @property
    def online_path(self):
        if self.url:
            return self.url

    def download(self, options=None):
        if options is None:
            options = getattr(self.model, 'options', None)
        if self.url:
            self.module.get_thumbnail(self.full_filename, self.url, options)

    def remove(self):
        local_path = self.local_path
        if local_path:
            os.remove(local_path)


def get_media_path(item):
    return os.path.join(DATA_PATH, 'medias', item.module_id, item.id)


def get_medias(item):
    try:
        return {Media(item, filename) for filename in os.listdir(get_media_path(item))}
    except FileNotFoundError:
        return set()


def remove_medias(item):
    try:
        rmtree(get_media_path(item))
    except FileNotFoundError:
        pass


class Media(object):
    def __init__(self, item, media_filename):
        self.item = item
        self.media_filename = media_filename
        self.filename = os.path.join('medias', item.module_id, item.id, media_filename)
        self.full_filename = os.path.join(DATA_PATH, self.filename)

    def __repr__(self):
        return '<Media "%s:%s" "%s">' % (self.item.module_id, self.item.id, self.media_filename)

    def remove(self):
        full_filename = self.full_filename
        if os.path.exists(full_filename):
            os.remove(full_filename)
