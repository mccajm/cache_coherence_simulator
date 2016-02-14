from cache import Cache


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

    def run_cycle(self):
        cpu_id, op, address = self.buses[self.cpu_id].get_nowait()
        super(MSICache, self).submit_msg(cpu_id, op, address)

