from cache import MESICache

shared_wire = False 
def play_traceline(cache, line):
    if line == "h":
        print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                          cache.stats["R"]["HIT"],
                                          cache.stats["W"]["HIT"]))
        return

    cpu_id, op, address = line.split(" ")
    cpu_id = int(cpu_id.lstrip("P"))
    address = int(address, 16)
    cache.submit_msg(cpu_id, op, address, shared_wire)


if __name__ == "__main__":
    num_cpus = 4
    caches = []
    for cpu_id in range(num_cpus):
        caches.append(MESICache(cpu_id))

    print("Reading file")
    with open("trace", "r") as f:
        for line in f:
            for cache in caches:
                play_traceline(cache, line)

    print("File read")
    for cache in caches:
        play_traceline(cache, "h")

