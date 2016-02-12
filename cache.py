import math


class Cache(object):

    def __init__(self, cpu_id, block_size=4):
        self.block_size = block_size  # assuming 32 bit architecture
        self.num_cache_lines = int(2048/self.block_size)
        self.offset_bits = int(math.log(self.block_size, 2))
        self.index_bits = int(math.log(self.num_cache_lines, 2))
        self.cpu_id = cpu_id
        self.stats = {"R": {"HIT": 0,
                            "MISS": 0,
                            "TOTAL": 0},
                      "W": {"HIT": 0,
                            "MISS": 0,
                            "TOTAL": 0},
                      "INVALIDATED": 0,
                      "UPDATED": 0}
        self._reset()

    def _map_address_to_block(self, address):
        binaddr = bin(address)[2:].zfill(32)
        offset = binaddr[-self.offset_bits:]
        index = int(binaddr[-(self.offset_bits + self.index_bits):-self.offset_bits], 2)
        tag = binaddr[:-(self.offset_bits + self.index_bits)]
        return index, tag

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
        if is_me:
            self.stats[op]["TOTAL"] += 1
            if self.store[index] == tag:
                if op == "W" and self.state_flags == "S":
                    self.stats[op]["MISS"] += 1
                else:
                    self.stats[op]["HIT"] += 1
                    hit = True
            else:
                self.stats[op]["MISS"] += 1
                self.store[index] = tag

        old_flag = self.state_flags[index]
        self.state_flags[index] = \
            self.state_transitions[op][is_me][self.state_flags[index]]
        if self.state_flags[index] == "I" and old_flag != "I":
            self.stats["INVALIDATED"] += 1

        return hit

 
class MSICache(Cache):

    def __init__(self, *args, **kwargs):
        self.reset_state = "I"
        self.state_transitions = {"R": {True: {"I": "S",
                                               "S": "S",
                                               "M": "M"},
                                        False: {"M": "S",
                                                "S": "S",
                                                "I": "I"}},
                                  "W": {True: {"I": "M",
                                               "S": "M",
                                               "M": "M"},
                                        False: {"S": "I",
                                                "M": "I",
                                                "I": "I"}}}
        super(MSICache, self).__init__(*args, **kwargs)


class MESICache(Cache):

    def __init__(self, *args, **kwargs):
        self.reset_state = "I"
        self.state_transitions = {"R": {True: {"I": "SE",
                                               "S": "S",
                                               "M": "M",
                                               "E": "E"},
                                        False: {"M": "S",
                                                "E": "S",
                                                "S": "S",
                                                "I": "I"}},
                                  "W": {True: {"I": "M",
                                               "S": "M",
                                               "M": "M",
                                               "E": "M"},
                                        False: {"S": "I",
                                                "M": "I",
                                                "I": "I",
                                                "E": "I"}}}
        super(MESICache, self).__init__(*args, **kwargs)

    def submit_msg(self, cpu_id, op, address, shared_wire):
        try:
            se_flag_key = self.state_flags.index("SE")
            if shared_wire:
                self.state_flags[se_flag_key] = "S"
                shared_wire = False
            else:
                self.state_flags[se_flag_key] = "E"
        except ValueError:
            pass  # no values are in SE state

        is_me = (cpu_id == self.cpu_id)
        if not is_me and op == "R":
            index, tag = self._map_address_to_block(address)
            if self.store[index] == tag:
                self.shared_wire = True

        super(MESICache, self).submit_msg(cpu_id, op, address)
        return shared_wire


class MESCache(Cache):

    def __init__(self, *args, **kwargs):
        self.reset_state = None
        self.state_transitions = {"R": {True: {"E": "E",
                                               "S": "S",
                                               "M": "E",
                                               None: "E"},
                                        False: {"M": "S",
                                                "E": "S",
                                                "S": "S",
                                                None: "E"}},
                                  "W": {True: {"E": "M",
                                               "M": "M",
                                               "S": "S",
                                               None: "E"},
                                        False: {"S": "S",
                                                "E": "S",
                                                "M": "S",
                                                None: "M"}}}
        super(MESCache, self).__init__(*args, **kwargs)

    def submit_msg(self, cpuid, op, address, update_wire):
        super(MESCache, self).submit_msg(cpuid, op, address)
        is_me = (cpuid == self.cpu_id)
        index, tag = self._map_address_to_block(address)
        update_wire[self.cpu_id] = None
        num_updates = len([v for v in update_wire if v is not None])
        self.stats["UPDATED"] += num_updates
        if op == "W" and self.state_flags[index] == "S":
            update_wire[self.cpu_id] = index

        return update_wire

