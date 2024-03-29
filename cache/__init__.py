import sys

from pprint import pprint

from utils import convert_to_binary


class Bus:
    """
    A simple atomic bus which distributes trace lines
    amongst the caches and allows the caches
    to query each other for state and updates.
    """

    def __init__(self, cache, num_caches, block_size=4):
        self.verbose = False
        self.hit_words = {True: "hit", False: "miss"}
        self.caches = []
        for i in range(num_caches):
            # Pass self into the new cache so that it can reach the bus
            self.caches.append(cache(i, self, block_size=block_size))

    def print_stats(self, op, address=None):
        if op == "v": # Toggle verbose output
            self.verbose = not self.verbose
            return

        for cache in self.caches:
            if op == "h":
                print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                                  cache.stats["R"]["HIT"],
                                                  cache.stats["W"]["HIT"]))
            elif op == "i":
                print("Invalidations P%d %d" % (cache.cpu_id,
                                                cache.stats["INVALIDATES"]))
            elif op == "p":
                print("P%d" % cache.cpu_id)
                if address:
                    index, _ = cache._map_address_to_block(address)
                    print("%d %d %s" % (index, cache.store[index], cache.state_flags[index]))
                else:
                    for index, state in enumerate(cache.state_flags):
                        print("%d %d %s" % (index, cache.store[index], state))

    def construct_verbose_message(self, cpu_id, op, address):
        """
        Builds a human readable representation of the current txn.
        """
        op_word = {"R": "read", "W": "write"}
        state_word = {"M": "Modified", "E": "Exclusive",
                      "S": "Shared", "I": "Invalid"}
 
        index, tag = self.caches[cpu_id]._map_address_to_block(address)
        this_state = self.caches[cpu_id].state_flags[index]
        address = int(address, 2)
        msg = "A %s by processor P%d to word %d looked for tag %d in cache-line/block %d, was found in state %s (cache %s) in this cache" % (op_word[op], cpu_id, address, tag, index, state_word[this_state], '%s')

        states = ((c.cpu_id, c.state_flags[index]) \
                      for c in self.caches \
                          if c.cpu_id != cpu_id)
        for i, state in states:
            msg += " and found in state %s in the cache of P%d" \
                       % (state_word[state], i)

        return "%s\n" % msg

    def process_transaction(self, cpu_id, op, address):
        """
        Processes trace lines. If they're read or write txns,
        they are distributed amongst the caches.
        """
        if op not in ("R", "W"):
            self.print_stats(op, address)
            return

        if self.verbose:
            verbose_msg = self.construct_verbose_message(cpu_id, op, address)

        for cache in self.caches:
            hit = cache.run(cpu_id, op, address)
            if self.verbose and cpu_id == cache.cpu_id:
                print(verbose_msg % self.hit_words[hit])

