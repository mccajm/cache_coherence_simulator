from threading import Thread
from queue import Queue

from cache import MSICache


class CPU(Thread):
    def __init__(self, bus, cache):
        Thread.__init__(self)
        self.bus = bus
        self.cache = cache
        a = 1

    def run(self):
        while True:
            item = self.bus.get()
            cpu_id, op, address = item.split(" ")
            cpu_id = int(cpu_id.lstrip("P"))
            address = int(address, 16)
            self.cache.submit_msg(cpu_id, op, address)
            self.bus.task_done()


if __name__ == "__main__":
    num_cpus = 4
    cpus = []
    buses = []
    caches = []
    for cpu_id in range(num_cpus):
        # For simplicity, I'm allocating a queue for
        #  each cache and replicating the trace
        buses.append(Queue())
        caches.append(MSICache(cpu_id))
        cpu = CPU(buses[cpu_id], caches[cpu_id])
        cpu.start()
        cpus.append(cpu)

    with open("trace", "r") as f:
        for line in f:
            for bus in buses: 
                bus.put(line)

    for cache in caches:
        print(cache.stats)

    for bus in buses:
        bus.join()
