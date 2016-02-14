from Queue import Empty 

from cache import Cache


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

    def stage1(self):
        while True:
            try:
                cpu_id, op, address = self.buses[self.cpu_id].get_nowait()
            except Empty:
                break  # the bus is empty

            is_me = (cpu_id == self.cpu_id)
            index, tag = self._map_address_to_block(address)
            if op == "S" and self.state_flags[index] in ("ES", "SM"):
                self.state_flags[index] = "S"
            elif not is_me and op == "R":
                if self.state_flags[index] in ("E", "S", "M"):
                    self.buses[cpu_id].put((self.cpu_id, "S", address))

        try:
            se_flag_index = self.state_flags.index("SE")
            self.state_flags[se_flag_index] = "E"
        except ValueError:
            pass

    def stage2(self, *args):
        super(MESICache, self).submit_msg(*args)

