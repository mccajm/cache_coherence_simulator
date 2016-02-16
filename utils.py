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

def parse_line(line):
    if len(line) == 1:
        return (None, line, None)

    cpu_id, op, address = line.split(" ")
    cpu_id = int(cpu_id.lstrip("P"))
    address = int(address, 16)
    binaddr = bin(address)[2:].zfill(32)
    return (cpu_id, op, binaddr)

