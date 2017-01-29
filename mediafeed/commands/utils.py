def bool_to_str(value):
    if value:
        return 'Sim'
    return 'Não'


def str_to_bool(value):
    return value.lower() in {'1', 'true'}
