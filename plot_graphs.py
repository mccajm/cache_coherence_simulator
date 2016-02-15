import pickle
import numpy

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
    fig = plt.figure()
    width = 0.2
    ax = fig.add_subplot(111)
    x = numpy.arange(4)
    for i, cache in enumerate(("MSICache", "MESICache", "MESCache")):
        ax.bar(x+width*(i-1), list(get_stats(stats[cache], "MISS")), width, color=plt.cm.coolwarm(i/4, 1), label=cache.rstrip("Cache"))

    ax.set_xlabel("Block Size")
    ax.set_ylabel("Miss Rate")
    ax.legend()
    ax.grid()
    ax.set_xticks(x+width/2)
    ax.set_xticklabels(2**(x+1))
    plt.title("Miss Rates at Different Block Sizes")
    plt.savefig("graphs/bs-miss.pdf")

def plot_hit():
    fig = plt.figure()
    width = 0.2
    ax = fig.add_subplot(111)
    x = numpy.arange(4)
    for i, cache in enumerate(("MSICache", "MESICache", "MESCache")):
        ax.bar(x+width*(i-1), list(get_stats(stats[cache], "HIT")), width, color=plt.cm.coolwarm(i/4, 1), label=cache.rstrip("Cache"))

    ax.set_xlabel("Block Size")
    ax.set_ylabel("Hit Rate")
    ax.legend(loc=4)
    ax.grid()
    ax.set_xticks(x+width/2)
    ax.set_xticklabels(2**(x+1))
    plt.title("Hit Rates at Different Block Sizes")
    plt.savefig("graphs/bs-hit.pdf")

def plot_invalidations():
    fig = plt.figure()
    width = 0.2
    ax = fig.add_subplot(111)
    x = numpy.arange(4)
    for i, cache in enumerate(("MSICache", "MESICache")):
        ax.bar(x+width*(i-1), list(get_stats_simple(stats[cache], "INVALIDATES")), width, color=plt.cm.coolwarm(i/4, 1), label=cache.rstrip("Cache"))

    ax.bar(x+width, list(get_stats_simple(stats["MESCache"], "WRITEUPDATES")), width, color=plt.cm.coolwarm(0.5, 1), label=cache.rstrip("Cache"))

    ax.set_xlabel("Block Size")
    ax.set_ylabel("Invalidations / Write Updates")
    ax.legend(loc=4)
    ax.grid()
    ax.set_xticks(x+width/2)
    ax.set_xticklabels(2**(x+1))
    plt.title("Invalidations and Updates at Different Block Sizes")
    plt.savefig("graphs/bs-invalidations_updates.pdf")

def plot_data_messages():
    fig = plt.figure()
    width = 0.2
    ax = fig.add_subplot(111)
    x = numpy.arange(4)
    for i, cache in enumerate(("MSICache", "MESICache", "MESCache")):
        wu = get_stats_simple(stats[cache], "WRITEUPDATES")
        wb = get_stats_simple(stats[cache], "WRITEBACK")
        total = [sum(x) for x in zip(wu, wb)]
        ax.bar(x+width*(i-1), total, width, color=plt.cm.coolwarm(i/4, 1), label=cache.rstrip("Cache"))
   
    ax.set_xlabel("Block Size")
    ax.set_ylabel("Data Messages")
    ax.legend(loc=5)
    ax.grid()
    ax.set_xticks(x+width/2)
    ax.set_xticklabels(2**(x+1))
    plt.title("Data Messages at Different Block Sizes")
    plt.savefig("graphs/bs-data.pdf")



print("Plotting graphs...")
plot_miss()
plot_hit()
plot_invalidations()
plot_data_messages()
