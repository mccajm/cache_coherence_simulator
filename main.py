from cache.msi import MSICache
from cache.mesi import MESICache
from cache.mes import MESCache


def int_or_None(i):
    try:
        return int(i, 2)
    except TypeError:
        return i 

shared_wire = False
update_wire = [None]*4
def play_traceline(cache, line):
    if line == "h":
        print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                          cache.stats["R"]["HIT"],
                                          cache.stats["W"]["HIT"]))
    elif line == "i":
        print("Invalidations P%d %d" % (cache.cpu_id,
                                        cache.stats["INVALIDATED"]))
    elif line == "p":
        print("Cache P%d %s" % (cache.cpu_id,
                                [int_or_None(v) for v in cache.store]))
    else:
        cpu_id, op, address = line.split(" ")
        cpu_id = int(cpu_id.lstrip("P"))
        address = int(address, 16)
        global update_wire, shared_wire
        shared_wire, update_wire = cache.submit_msg(cpu_id, op, address, shared_wire, update_wire)


if __name__ == "__main__":
    for cache in (MSICache, MESICache, MESCache):
        caches = []
        for cpu_id in range(4):
            caches.append(cache(cpu_id))

        print("Reading file")
        with open("trace", "r") as f:
            for line in f:
                for cache in caches:
                    play_traceline(cache, line)

        print("File read")
        for cache in caches:
            play_traceline(cache, "h")

        for cache in caches:
            play_traceline(cache, "i")

