from multiprocessing import Queue, Process

from cache import MSICache


class CPU(Process):
    def __init__(self, bus, cache, cpu_id):
        Process.__init__(self)
        self.bus = bus
        self.cache = cache(cpu_id)

    def run(self):
        while True:
            item = self.bus.get()
            if item == None:
                break
            elif item == "h":
                print("Hit Rate P%d R:%d W:%d" % (self.cache.cpu_id,
                                                   self.cache.stats["R"]["HIT"],
                                                   self.cache.stats["W"]["HIT"]))
                continue

            cpu_id, op, address = item.split(" ")
            cpu_id = int(cpu_id.lstrip("P"))
            address = int(address, 16)
            self.cache.submit_msg(cpu_id, op, address)


if __name__ == "__main__":
    num_cpus = 4
    cpus = []
    buses = []
    for cpu_id in range(num_cpus):
        # For simplicity, I'm allocating a queue for
        #  each cache and replicating the trace
        buses.append(Queue())
        cpu = CPU(buses[cpu_id], MSICache, cpu_id)
        cpu.start()
        cpus.append(cpu)
        print("Spawned CPU %d" % cpu_id)

    print("Reading file")
    with open("trace", "r") as f:
        for line in f:
            for bus in buses: 
                bus.put(line)

    print("File read")
    for bus in buses:
        bus.put("h")
        bus.put(None)

    for cpu in cpus:
        cpu.join()

