from cache.protocols import Cache


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

    def run(self, cpu_id, op, address):
        _, _, hit = super(MSICache, self).submit_msg(cpu_id, op, address)

        return hit

