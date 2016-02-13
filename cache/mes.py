from cache import Cache


class MESCache(Cache):

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

    def submit_msg(self, cpuid, op, address, shared_wire, update_wire):
        index, tag = self._map_address_to_block(address)
        try:
            es_flag_key = self.state_flags.index("ES")
            if shared_wire:
                self.state_flags[es_flag_key] = "S"
                shared_wire = false
            else:
                self.state_flags[es_flag_key] = "E"
        except ValueError:
            pass  # no values are in es state

        try:
            sm_flag_key = self.state_flags.index("SM")
            if shared_wire:
                self.state_flags[sm_flag_key] = "S"
                shared_wire = false
            else:
                self.state_flags[sm_flag_key] = "M"
        except ValueError:
            pass  # no values are in sm state

        hit = super(MESCache, self).submit_msg(cpuid, op, address)
        is_me = (cpuid == self.cpu_id)
        update_wire[self.cpu_id] = None
        updates = [v for v in update_wire if v is not None]
        self.stats["UPDATED"] += len(updates)
        for update in updates:
            index_update, tag_update = self._map_address_to_block(update)
            self.store[index_update] = tag_update
            self.state_flags[index_update] = "S"

        if op == "W" and self.state_flags[index] == "S":
            update_wire[self.cpu_id] = address 
        elif not hit:
            if op == "R":
                self.state_flags[index] = "ES"
            else:
                self.state_flags[index] = "SM"

        return shared_wire, update_wire

