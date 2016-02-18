from os import listdir

from nose.tools import with_setup, assert_equal

from cache import Bus
from cache.protocols.msi import MSICache
from cache.protocols.mesi import MESICache
from cache.protocols.mes import MESCache
from utils import parse_line, convert_to_binary


def parse_end_state(line):
    line = line.rstrip("\n").split(": ")[1]
    index, states = line.split(";")
    states = states.split(",")
    return (index, states)

def states_match(expected_end_states, bus):
    for address, states in expected_end_states:
        binaddr = convert_to_binary(address)
        index, _ = bus.caches[0]._map_address_to_block(binaddr)
        end_states = ["%s" % c.state_flags[index] for c in bus.caches]
        assert_equal(states, end_states)

def run_trace(bus, f):
    expected_end_states = []
    for line in f:
        if line.startswith("#"):
            if line.find("EndState:") != -1:
                expected_end_states.append(parse_end_state(line))
                
            continue
    
        line = parse_line(line)
        bus.process_transaction(*line)

    states_match(expected_end_states, bus)

def test_all_traces():
    cache_by_name = {"msi": MSICache,
                     "mesi": MESICache,
                     "mes": MESCache}
    for trace in listdir("tests/traces"):
        name = trace.split("_")[0]
        bus = Bus(cache_by_name[name], 4)
        with open("tests/traces/%s" % trace) as f:
            yield run_trace, bus, f

