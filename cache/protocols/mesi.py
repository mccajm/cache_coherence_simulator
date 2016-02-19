from cache.protocols import Cache


class MESICache(Cache):
    """
    Implements the MESI protocol by setting the reset_state
    and defining state_transitions.
    Exclusive transitions are handled in run(...).
    """

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

    def run(self, cpu_id, op, address):
        index, _, hit = super(MESICache, self).submit_msg(cpu_id, op, address)
        # SE transition state means we need to do further processing
        if self.state_flags[index] == "SE":
            other_cpus = (i for i in range(4) if i != self.cpu_id)
            for cpu_id in other_cpus:
                # If another cache has this block, set them and us to S
                if self.bus.caches[cpu_id].state_flags[index] in ("E", "S", "M"):
                    self.state_flags[index] = "S"
                    self.bus.caches[cpu_id].state_flags[index] = "S"

            # No other cache had this block so E
            if self.state_flags[index] == "SE":
                self.state_flags[index] = "E"

        return hit

