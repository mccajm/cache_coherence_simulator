from cache import MSICache

shared_wire = False
update_wire = [None]*4
def play_traceline(cache, line):
    if line == "h":
        print("Hit Rate P%d R:%d W:%d" % (cache.cpu_id,
                                          cache.stats["R"]["MISS"],
                                          cache.stats["W"]["MISS"]))
        return

    cpu_id, op, address = line.split(" ")
    cpu_id = int(cpu_id.lstrip("P"))
    address = int(address, 16)
    global update_wire, shared_wire
    cache.submit_msg(cpu_id, op, address)


if __name__ == "__main__":
    caches = []
    for cpu_id in range(4):
        caches.append(MSICache(cpu_id))

    print("Reading file")
    with open("trace", "r") as f:
        for line in f:
            for cache in caches:
                play_traceline(cache, line)

    print("File read")
    for cache in caches:
        play_traceline(cache, "h")

