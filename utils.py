def int_or_None(i):
    try:
        return int(i, 2)
    except TypeError:
        return i

def nested_dict_values(d):
    for v in d.values():
        if isinstance(v, dict):
            for v in nested_dict_values(v):
                yield v
        else:
            yield v

