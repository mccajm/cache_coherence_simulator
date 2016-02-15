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

    def stage1(self):
        while True:
            try:
                cpu_id, op, address = self.buses[self.cpu_id].pop()
            except IndexError:
                break  # the bus is empty

            is_me = (cpu_id == self.cpu_id)
            index, tag = self._map_address_to_block(address)
            if op == "S" and self.state_flags[index] in ("ES", "SM"):
                self.state_flags[index] = "S"
                self.stats["WRITEBACK"] += 1
            elif not is_me and op == "R":
                if self.state_flags[index] in ("E", "S", "M"):
                    self.buses[cpu_id].append((self.cpu_id, "S", address))
            elif op == "U":
                self.store[index] = tag
                self.state_flags[index] = "S"
                self.stats["WRITEUPDATED"] += 1

        try:
            es_flag_index = self.state_flags.index("ES")
            self.state_flags[es_flag_index] = "E"
        except ValueError:
            pass

        try:
            sm_flag_index = self.state_flags.index("SM")
            self.state_flags[sm_flag_index] = "M"
        except ValueError:
            pass

    def stage2(self, cpu_id, op, address):
        hit = super(MESCache, self).submit_msg(cpu_id, op, address)
        is_me = (cpu_id == self.cpu_id)
        if not is_me:
            return

        index, _ = self._map_address_to_block(address)
        if op == "W" and self.state_flags[index] == "S":
            self.stats["WRITEBACK"] += 1
            other_buses = [i for i in range(len(self.buses)) if i != self.cpu_id]
            for bus_id in other_buses:
                self.buses[bus_id].append((self.cpu_id, "U", address))

            self.stats["WRITEUPDATES"] += 1
        elif not hit:
            if op == "R":
                self.state_flags[index] = "ES"
            else:
                self.state_flags[index] = "SM"

