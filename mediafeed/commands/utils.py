from functools import wraps

from ..databases import Session


__all__ = ('with_db',)


def with_db(command):
    @wraps(command)
    def wrapper(*args, **kwargs):
        if kwargs.get('db') is None:
            db = Session()
            kwargs['db'] = db
        else:
            db = None
        result = command(*args, **kwargs)
        if db:
            db.close()
        return result
    return wrapper
