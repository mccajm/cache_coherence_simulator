from os import listdir

from nose.tools import with_setup, assert_equal

from cache import Bus
from cache.protocols.msi import MSICache
from cache.protocols.mesi import MESICache
from cache.protocols.mes import MESCache
from utils import parse_line, convert_to_binary


def parse_end_state(line):
    line = line.split(": ")[1].split(";")
    index = line[0]
    states = line[1].split(",")
    states[-1] = states[-1].rstrip("\n")
    return (index, states)


class testCache:

    def states_match(self):
        address, states = self.expected_end_state
        binaddr = convert_to_binary(address)
        index, _ = self.bus.caches[0]._map_address_to_block(binaddr)
        end_states = [c.state_flags[index] for c in self.bus.caches]
        assert_equal(states, end_states)

    def run_trace(self, bus, f):
        self.bus = bus
        self.expected_end_state = None
        for line in f:
            if not self.expected_end_state:
                self.expected_end_state = parse_end_state(line)
                continue
        
            line = parse_line(line)
            self.bus.process_transaction(*line)

        self.states_match()

    def test_all_traces(self):
        cache_by_name = {"msi": MSICache,
                         "mesi": MESICache,
                         "mes": MESCache}
        for trace in listdir("tests/traces"):
            name = trace.split("_")[0]
            bus = Bus(cache_by_name[name], 4)
            with open("tests/traces/%s" % trace) as f:
                yield self.run_trace, bus, f

