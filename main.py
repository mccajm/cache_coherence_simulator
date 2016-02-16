import sys
import pickle

from pprint import pprint

from tqdm import tqdm

from cache import Bus
from cache.protocols.msi import MSICache
from cache.protocols.mesi import MESICache
from cache.protocols.mes import MESCache
from utils import int_or_None, parse_line


stats = {"MSICache": {},
         "MESICache": {},
         "MESCache": {}}
def record_stats(caches):
    global stats
    for cache in caches:
        stats[cache.__class__.__name__][cache.block_size] = cache.stats

if __name__ == "__main__":
    with open("trace", "r") as f:
        lines = f.readlines()

    block_sizes = (2, 4, 8, 16)
    for cache in (MSICache, MESICache, MESCache):
        for block_size in block_sizes:
            bus = Bus(cache, 4, block_size=block_size)

            print("Processing trace with %s at block size %d..." % (bus.caches[-1].__class__.__name__, block_size))
            for line in tqdm(lines, leave=True):
                line = parse_line(line)
                bus.process_transaction(*line)

            record_stats(bus.caches)

    with open("stats-block_size.pkl", "wb") as f:
        pickle.dump(stats, f)
