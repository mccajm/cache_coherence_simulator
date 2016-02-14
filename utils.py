def int_or_None(i):
    try:
        return int(i, 2)
    except TypeError:
        return i
