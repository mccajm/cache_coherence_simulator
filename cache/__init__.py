import sys

from pprint import pprint


class Bus:

    def __init__(self, cache, num_caches, block_size=4):
        self.caches = []
        for i in range(num_caches):
            self.caches.append(cache(i, self, block_size=block_size))

    def print_stats(self, op):
        for cache in self.caches:
            if op == "h":
                print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                                  cache.stats["R"]["HIT"],
                                                  cache.stats["W"]["HIT"]))
            elif op == "i":
                print("Invalidations P%d %d" % (cache.cpu_id,
                                                cache.stats["INVALIDATES"]))
            elif op == "p":
                print("Cache P%d %s" % (cache.cpu_id,
                                        [int_or_None(v) for v in cache.store]))
            elif op == "s":
                sys.stdout.write("P%d: " % cache.cpu_id)
                pprint(cache.stats)

    def process_transaction(self, cpu_id, op, address):
        if op not in ("R", "W"):
            print_stats(op)
            return

        for cache in self.caches:
            cache.run(cpu_id, op, address)

