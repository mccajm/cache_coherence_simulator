from cache.protocols import Cache


class MESCache(Cache):
    """
    Implements the MES update-based protocol by defining reset_state
    and state transitions. Write updates are handled in run(...).
    """

    def __init__(self, *args, **kwargs):
        self.reset_state = None
        self.state_transitions = {"R": {True: {"E": "E",
                                               "S": "S",
                                               "M": "M",
                                               None: None},
                                        False: {"M": "S",
                                                "E": "S",
                                                "S": "S",
                                                None: None}},
                                  "W": {True: {"E": "M",
                                               "M": "M",
                                               "S": "S",
                                               None: None},
                                        False: {"S": "S",
                                                "E": "S",
                                                "M": "S",
                                                None: None}}}
        super(MESCache, self).__init__(*args, **kwargs)

    def run(self, cpu_id, op, address):
        index, tag, hit = super(MESCache, self).submit_msg(cpu_id, op, address)
        is_me = (cpu_id == self.cpu_id)
        if is_me:
            if hit: # If we hit we need to do further processing
                if self.state_flags[index] == "M":
                    self.stats["WRITEBACK"] += 1
                elif op == "W" and self.state_flags[index] == "S":
                    self.stats["WRITEBACK"] += 1
                    self.stats["WRITEUPDATES"] += 1
                    other_cpus = (i for i in range(len(self.bus.caches)) if i != self.cpu_id)
                    for cpu_id in other_cpus: # Send write-update messages
                        self.bus.caches[cpu_id].store[index] = tag
                        self.bus.caches[cpu_id].state_flags[index] = "S"
                        self.bus.caches[cpu_id].stats["WRITEUPDATED"] += 1
            else:
                other_cpus = (i for i in range(len(self.bus.caches)) if i != self.cpu_id)
                # If we missed and another state has the block, we're shared
                # The other cache will update their state based on the transition
                for cpu_id in other_cpus:
                    if self.bus.caches[cpu_id].state_flags[index] in ("E", "S", "M"):
                        self.state_flags[index] = "S"
                        break
                else: # Another cache didn't have the block
                    if op == "R":
                        self.state_flags[index] = "E"
                    else:
                        self.state_flags[index] = "M"
    
        return hit

