import os

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
