import sys

from pprint import pprint

from utils import convert_to_binary


class Bus:

    def __init__(self, cache, num_caches, block_size=4):
        self.caches = []
        for i in range(num_caches):
            c = cache(i, self, block_size=block_size)
            self.caches.append(c)

    def print_stats(self, op, address=None):
        address = convert_to_binary(address)
        for cache in self.caches:
            if op == "h":
                print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                                  cache.stats["R"]["HIT"],
                                                  cache.stats["W"]["HIT"]))
            elif op == "i":
                print("Invalidations P%d %d" % (cache.cpu_id,
                                                cache.stats["INVALIDATES"]))
            elif op == "p":
                if address:
                    index, _ = cache._map_address_to_block(address)
                    data = cache.state_flags[index]
                else:
                    data = cache.state_flags

                print("P%d %s" % (cache.cpu_id, data))
            elif op == "s":
                sys.stdout.write("P%d: " % cache.cpu_id)
                pprint(cache.stats)

    def process_transaction(self, cpu_id, op, address):
        if op not in ("R", "W"):
            self.print_stats(op, address)
            return

        for cache in self.caches:
            cache.run(cpu_id, op, address)

