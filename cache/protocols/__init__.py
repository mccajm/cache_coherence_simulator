import math

from utils import nested_dict_values


class Cache(object):
    """
    This class takes a set of state transitions as a nested dictionary (hash table) in
    the form
    [op][is me][current state] → new state (1)
    where op is the operation performed (R or W), is me is a Boolean flag representing
    whether the bus transaction is related to the current cache and current state
    is the current state of the line upon which the transaction has been performed.
    Additionally, this class records statistics and updates the tag stored in a
    cache line in the event of a miss. Finally, it sets the initial state of all blocks to
    be a defined reset state.
    """

    def __init__(self, cpu_id, bus, block_size=4):
        self.block_size = block_size
        self.num_cache_lines = int(2048/self.block_size)
        self.offset_bits = int(math.log(self.block_size, 2))
        self.index_bits = int(math.log(self.num_cache_lines, 2))
        self.cpu_id = cpu_id
        self.bus = bus
        self.stats = {"R": {"HIT": 0,
                            "HIT_PRIV": 0,
                            "MISS": 0,
                            "TOTAL": 0},
                      "W": {"HIT": 0,
                            "HIT_PRIV": 0,
                            "MISS": 0,
                            "TOTAL": 0},
                      "INVALIDATES": 0,
                      "INVALIDATED": 0,
                      "WRITEUPDATES": 0,
                      "WRITEUPDATED": 0,
                      "WRITEBACK": 0}
        # If the state transitions contain an Invalid state,
        #   this is an invalidation-based protocol
        self.invalidation_based = \
            ("I" in nested_dict_values(self.state_transitions))
        self._reset()

    def _map_address_to_block(self, address):
        """
        Extracts the index and tag from the supplied address.
        """
        index = int(address[-(self.offset_bits + self.index_bits):-self.offset_bits], 2)
        tag = int(address[:-(self.offset_bits + self.index_bits)], 2)
        return (index, tag)

    def _reset(self):
        try:
            self.store = []
            self.state_flags = []
            for index in range(self.num_cache_lines):
                self.store.append(None)
                self.state_flags.append(self.reset_state)
        except NameError:
            raise Exception("Cache class must be subclassed with"
                            "definitions for reset_state and"
                            "state_transitions")

    def submit_msg(self, cpu_id, op, address):
        is_me = (cpu_id == self.cpu_id)
        index, tag = self._map_address_to_block(address)
        hit = False
        if is_me: # Metrics recording
            self.stats[op]["TOTAL"] += 1
            if (self.state_flags[index] != "I") and not \
               (op == "W" and self.state_flags == "S") and \
               (self.store[index] == tag):
                self.stats[op]["HIT"] += 1
                if self.state_flags[index] in ("M", "E"):
                    self.stats[op]["HIT_PRIV"] += 1
                hit = True
            else:
                self.stats[op]["MISS"] += 1
                # We missed so update the stored value
                self.store[index] = tag

        old_flag = self.state_flags[index]
        # Follow the state transition
        self.state_flags[index] = \
            self.state_transitions[op][is_me][self.state_flags[index]]

        # Further metrics recording
        if self.state_flags[index] == "I" and old_flag != "I":
            self.stats["INVALIDATED"] += 1
        elif self.invalidation_based and \
             self.state_flags[index] == "M" and old_flag not in ("M", "E"):
            self.stats["WRITEBACK"] += 1
        elif not self.invalidation_based and \
            self.state_flags[index] == "S" and old_flag == "M":
            self.stats["WRITEBACK"] += 1

        if self.invalidation_based and is_me and op == "W":
            self.stats["INVALIDATES"] += 1

        return (index, tag, hit)

