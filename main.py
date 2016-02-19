###########################
# Cache Coherence Simulator
# Author: Adam McCarthy
###########################
import pickle
import sys

from argparse import ArgumentParser, RawTextHelpFormatter

from tqdm import tqdm

from cache import Bus
from cache.protocols.msi import MSICache
from cache.protocols.mesi import MESICache
from cache.protocols.mes import MESCache
from utils import int_or_None, parse_line


def record_stats(stats, caches):
    """
    Records the stats for each cache
    """
    for cache in caches:
        stats[cache.__class__.__name__][cache.block_size] = cache.stats

if __name__ == "__main__":
    parser = ArgumentParser(description="Cache Coherence Simulator.", formatter_class=RawTextHelpFormatter)
    parser.add_argument("--noprogress", dest="noprogress", action="store_true", help="hide the progress bar (required if printing stats)")
    parser.add_argument("filename", metavar="filename", type=str, nargs=1, help="the trace file to process")
    parser.add_argument("--msi", dest="msi", action="store_const", const=MSICache, default=None, help="simulate the MSI protocol")
    parser.add_argument("--mesi", dest="mesi", action="store_const", const=MESICache, default=None, help="simulate the MESI protocol")
    parser.add_argument("--mes", dest="mes", action="store_const", const=MESCache, default=None, help="simulate the MES protocol")
    parser.add_argument("--record", dest="record", action="store_true", help="record statistics to a file")

    args = parser.parse_args()
    caches = (args.msi, args.mesi, args.mes)
    caches = [c for c in caches if c is not None]
    if len(caches) == 0:
        sys.stderr.write("Please choose at least one cache.\n")
        sys.exit(1)

    with open(args.filename[0], "r") as f:
        trace_lines = f.readlines()

    block_sizes = (2, 4, 8, 16)
    stats = {}
    for cache in caches:
        if args.record:
            stats[cache.__name__] = {}

        for block_size in block_sizes:
            # Create an atomic bus with 4 caches
            bus = Bus(cache, 4, block_size=block_size)

            print("Processing trace with %s at block size %d..." % (cache.__name__, block_size))
            if not args.noprogress:
                # Create a progressbar
                pbar = tqdm(total=len(trace_lines), leave=True)

            for line in trace_lines:
                # convert "P0 R 2 into (0, "R", 2)
                line = parse_line(line)
                if not args.noprogress:
                    pbar.update(1)

                if line: # ignore comments (which are None)
                    bus.process_transaction(*line)

            if not args.noprogress:
                pbar.close()

            if args.record:
                record_stats(stats, bus.caches)

    if args.record:
        with open("stats-block_size.pkl", "wb") as f:
            pickle.dump(stats, f)
