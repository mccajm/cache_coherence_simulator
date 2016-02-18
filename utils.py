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

def convert_to_binary(i):
    address = int(i, 16)
    return bin(address)[2:].zfill(32)

def parse_line(line):
    line = line.split(" ")
    if len(line) == 1:
        op = line[0]
        return (None, op, None)
    elif len(line) == 2:
        op, address = line
        return (None, op, address)

    cpu_id, op, address = line
    cpu_id = int(cpu_id.lstrip("P"))
    binaddr = convert_to_binary(address)
    return (cpu_id, op, binaddr)

