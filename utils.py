def int_or_None(i):
    try:
        return int(i, 2)
    except TypeError:
        return i

def nested_dict_values(d):
    """
    Returns all values from a nested dict.
    """
    for v in d.values():
        if isinstance(v, dict):
            for v in nested_dict_values(v):
                yield v
        else:
            yield v

def convert_to_binary(i):
    address = int(i, 16)
    return bin(address)[2:].zfill(32)

def parse_line(line):
    """
    Parses trace lines
    e.g. P0 R 2 => (0, "R", 2)
    e.g. p => (None, "p", None)
    """
    if line.startswith("#") or len(line) == 0:
        return None  # comment or blank line

    line = line.split(" ")
    if len(line) == 1: # e.g. p
        op = line[0]
        return (None, op.rstrip("\n"), None)
    elif len(line) == 2: # e.g. p 2
        op, address = line
        return (None, op, address)

    # e.g. P0 R 2
    cpu_id, op, address = line
    cpu_id = int(cpu_id.lstrip("P"))
    binaddr = convert_to_binary(address)
    return (cpu_id, op, binaddr)

