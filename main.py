import pickle
import sys

from tqdm import tqdm

from cache import Bus
from cache.protocols.msi import MSICache
from cache.protocols.mesi import MESICache
from cache.protocols.mes import MESCache
from utils import int_or_None, parse_line


def record_stats(stats, caches):
    for cache in caches:
        stats[cache.__class__.__name__][cache.block_size] = cache.stats

if __name__ == "__main__":
    try:
        trace_file = sys.argv[1]
    except IndexError:
        print("Please supply a trace file as an argument.")
        sys.exit(1)

    progress_bar = 1
    try:
        progress_bar = int(sys.argv[2])
    except IndexError:
        pass

    with open(trace_file, "r") as f:
        lines = f.readlines()

    block_sizes = (2, 4, 8, 16)
    stats = {}
    for cache in (MSICache, MESICache, MESCache):
        cache_name = str(cache).split("'")[1].split(".")[-1]
        stats[cache_name] = {}
        for block_size in block_sizes:
            bus = Bus(cache, 4, block_size=block_size)

            print("Processing trace with %s at block size %d..." % (cache_name, block_size))
            if progress_bar == 1:
                pbar = tqdm(total=len(lines), leave=True)

            for line in lines:
                line = parse_line(line)
                if progress_bar == 1:
                    pbar.update(1)

                if line:
                    bus.process_transaction(*line)

            if progress_bar == 1:
                pbar.close()

            record_stats(stats, bus.caches)

    with open("stats-block_size.pkl", "wb") as f:
        pickle.dump(stats, f)
