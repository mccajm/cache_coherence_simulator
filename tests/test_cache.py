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

def states_match(expected_end_state, bus):
    address, states = expected_end_state
    binaddr = convert_to_binary(address)
    index, _ = bus.caches[0]._map_address_to_block(binaddr)
    end_states = [c.state_flags[index] for c in bus.caches]
    assert_equal(states, end_states)

def run_trace(bus, f):
    expected_end_state = None
    for line in f:
        if not expected_end_state:
            expected_end_state = parse_end_state(line)
            continue
    
        line = parse_line(line)
        bus.process_transaction(*line)

    states_match(expected_end_state, bus)

def test_all_traces():
    cache_by_name = {"msi": MSICache,
                     "mesi": MESICache,
                     "mes": MESCache}
    for trace in listdir("tests/traces"):
        name = trace.split("_")[0]
        bus = Bus(cache_by_name[name], 4)
        with open("tests/traces/%s" % trace) as f:
            yield run_trace, bus, f

