import pickle

import matplotlib.pyplot as plt

def get_stats(stats, key):
    for bs in (2,4,8,16):
        yield stats[bs]["R"][key] + stats[bs]["W"][key]

def get_stats_simple(stats, key):
    for bs in (2,4,8,16):
        yield stats[bs][key]


with open("stats-block_size.pkl", "rb") as f:
    stats = pickle.load(f)

def plot_miss():
    for cache in ("MSICache", "MESICache", "MESCache"):
        plt.plot([2,4,8,16], list(get_stats(stats[cache], "MISS")), label=cache)

    plt.legend()
    plt.grid()
    plt.title("Miss Rates at different block sizes")
    plt.savefig("graphs/bs-miss.pdf")

def plot_hit():
    for cache in ("MSICache", "MESICache", "MESCache"):
        plt.plot([2,4,8,16], list(get_stats(stats[cache], "HIT")), label=cache)

    plt.legend(loc=4)
    plt.grid()
    plt.title("Hit Rates at different block sizes")
    plt.savefig("graphs/bs-hit.pdf")

def plot_invalidations():
    for cache in ("MSICache", "MESICache"):
        plt.plot([2,4,8,16], list(get_stats_simple(stats[cache], "INVALIDATES")), label=cache)

    plt.plot([2,4,8,16], list(get_stats_simple(stats["MESCache"], "WRITEUPDATES")), label="MESCache")

    plt.legend(loc=5)
    plt.grid()
    plt.title("Invalidations and Updates at different block sizes")
    plt.savefig("graphs/bs-invalidations_updates.pdf")

def plot_data_messages():
    for cache in ("MSICache", "MESICache", "MESCache"):
        wu = get_stats_simple(stats[cache], "WRITEUPDATES")
        wb = get_stats_simple(stats[cache], "WRITEBACK")
        total = [sum(x) for x in zip(wu, wb)]
        plt.plot([2,4,8,16], total, label=cache)
    
    plt.legend(loc=5)
    plt.grid()
    plt.title("Data Messages at different block sizes")
    plt.savefig("graphs/bs-data.pdf")



plt.figure()
plot_miss()
plt.figure()
plot_hit()
plt.figure()
plot_invalidations()
plt.figure()
plot_data_messages()
