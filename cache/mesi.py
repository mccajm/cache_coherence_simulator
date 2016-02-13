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

    def submit_msg(self, cpu_id, op, address, shared_wire, update_wire):
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
            if self.state_flags[index] == "E" or self.state_flags[index] == "S" or self.state_flags[index] == "M":
                self.shared_wire = True

        super(MESICache, self).submit_msg(cpu_id, op, address)
        return shared_wire, update_wire

