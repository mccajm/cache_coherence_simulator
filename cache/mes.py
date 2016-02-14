from Queue import Empty

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

    def run_cycle(self):
        backup_messages = []
        read_miss_msg = None
        while True:
            try:
                cpu_id, op, address = self.buses[self.cpu_id].get_nowait()
            except Empty:
                break  # the bus is empty

            is_me = (cpu_id == self.cpu_id)
            if op == "S":
                msg_expected = False
                index, tag = self._map_address_to_block(address)
                try:
                    es_flag_index = self.state_flags.index("ES")
                    if index == es_flag_index:
                        message_expected = True
                        self.state_flags[es_flag_index] = "S"
                except ValueError:
                    try:
                        sm_flag_index = self.state_flags.index("SM")
                        if index == sm_flag_index:
                            message_expected = True
                            self.state_flags[sm_flag_index] = "S"
                    except ValueError:
                        pass  # no values are in ES or SM state

                if not msg_expected:  # Received early
                    backup_messages.append((cpu_id, op, address))
            elif not is_me and op == "R":
                index, tag = self._map_address_to_block(address)
                if self.state_flags[index] in ("E", "S", "M"):
                    self.buses[cpu_id].put((self.cpu_id, "S", address))
            elif op == "U":
                index_update, tag_update = self._map_address_to_block(address)
                self.store[index_update] = tag_update
                self.state_flags[index_update] = "S"

            if op in ("R", "W"):
                # This ensures we always process the read_miss_msg last
                read_miss_msg = (cpu_id, op, address)

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

        for msg in backup_messages[:-1]:
            self.buses[self.cpu_id].put(msg)

        cpu_id, op, address = read_miss_msg
        hit = super(MESCache, self).submit_msg(cpu_id, op, address)
        index, tag = self._map_address_to_block(address)
        if is_me and op == "W" and self.state_flags[index] == "S":
            other_buses = [i for i in range(len(self.buses)) if i != self.cpu_id]
            for bus_id in other_buses:
                self.stats["WRITEBACK"] += 1
                self.buses[bus_id].put((self.cpu_id, "U", address))

            self.stats["UPDATED"] += 1
        elif is_me and not hit:
            if op == "R":
                self.state_flags[index] = "ES"
            else:
                self.state_flags[index] = "SM"

