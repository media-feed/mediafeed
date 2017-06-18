__all__ = ('read_bool', 'read_int')


def read_bool(value, default=None):
    if value is None:
        return default
    return value.lower() in {'1', 'on', 'true'}


def read_int(value, default=None):
    if value is None or value.lower() in {'none', 'null'}:
        return default
    return int(value)
