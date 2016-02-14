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

    def run_cycle(self):
        backup_messages = []
        read_miss_msg = None
        while True:
            try:
                cpu_id, op, address = self.buses[self.cpu_id].get_nowait()
            except Empty:
                break  # the bus is empty

            is_me = (cpu_id == self.cpu_id)
            if is_me and op == "S":
                msg_expected = False
                index, tag = self._map_address_to_block(address)
                try:
                    se_flag_index = self.state_flags.index("SE")
                    if index == se_flag_index:
                        message_expected = True
                        self.state_flags[se_flag_index] = "S"
                except ValueError:
                    pass

                if not msg_expected and self.state_flags[index] == "I":  # Received early
                    backup_messages.append((cpu_id, op, address))
            elif not is_me and op == "R":
                index, tag = self._map_address_to_block(address)
                if self.state_flags[index] == "E" or self.state_flags[index] == "S" or self.state_flags[index] == "M":
                    self.buses[cpu_id].put((cpu_id, "S", address))

            if op == "R" or op == "W":
                # This ensures we always process the read_miss_msg last
                read_miss_msg = (cpu_id, op, address)

        try:
            se_flag_index = self.state_flags.index("SE")
            self.state_flags[se_flag_index] = "E"
        except ValueError:
            pass

        for msg in backup_messages:
            self.buses[self.cpu_id].put(msg)

        super(MESICache, self).submit_msg(*read_miss_msg)

