import threading

import redis

from cache import MSICache


class CPU(threading.Thread):
    def __init__(self, r, cache):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("cachebus")
        self.cache = cache

    def work(self, msg):
        print(item['data'])

    def run(self):
        for item in self.pubsub.listen():
            self.work(item)


if __name__ == "__main__":
    r = redis.Redis()
    
    num_cpus = 4
    cpus = []
    for i in num_cpus:
        client = Listener(r, MSICache())
        client.start()

