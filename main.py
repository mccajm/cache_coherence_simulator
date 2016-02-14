import sys

from pprint import pprint
from Queue import Queue

from tqdm import tqdm

from cache.msi import MSICache
from cache.mesi import MESICache
from cache.mes import MESCache
from utils import int_or_None


buses = (Queue(), Queue(), Queue(), Queue())
def print_stats(cache, line):
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
    elif line == "s":
        sys.stdout.write("P%d: " % cache.cpu_id)
        pprint(cache.stats)

def parse_line(line):
    if len(line) == 1:
        return (None, line, None)

    cpu_id, op, address = line.split(" ")
    cpu_id = int(cpu_id.lstrip("P"))
    address = int(address, 16)
    return (cpu_id, op, address)

def run_stages(caches, cpu_id, op, address):
    for cache in caches:
        cache.stage1()

    if op in ("R", "W"):
        for cache in caches:
            cache.stage2(cpu_id, op, address)


if __name__ == "__main__":
    with open("trace", "r") as f:
        lines = f.readlines()

    for cache in (MSICache, MESICache, MESCache):
        caches = []
        for cpu_id in range(4):
            caches.append(cache(cpu_id, buses))

        print("Processing trace with %s..." % caches[-1].__class__.__name__)
        for line in tqdm(lines, leave=True):
            cpu_id, op, address = parse_line(line)
            if op in ("h", "i", "p", "s"):
                for cache in caches:
                    print_stats(cache, op)
            else:
                run_stages(caches, cpu_id, op, address)

        for cache in caches:
            print_stats(cache, "s")

