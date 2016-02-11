import inspect


class CacheMissException(Exception):
    pass

class Cache(list):

    def __init__(self, block_size=4):
        self.block_size = block_size*32  # assuming 32 bit architecture
        self.max_value = 2**block_size
        self.num_cache_lines = 2048/block_size
        self.state_flags = []
        self.stat_misses = 0
        self.parent = parent
        super(Cache, self).__init__(*args, **kwargs)
        self.reset()

    def _check_cache_size(self):
        if len(self) >= self.num_cache_lines:
            raise IndexError

    def _check_block_size(self, b):
        if len(v) != self.block_size:
            raise ValueError

    def _check_new_cache_size(self, L):
        if len(self) + len(L) > self.num_cache_lines:
            raise IndexError

    def _check_is_binary(self, b):
        if not all((v==0 or v==1) for v in b):
            raise ValueError

    def _map_address_to_block(self, i):
        return i
    
    def append(self, x):
        raise NotImplementedError

    def extend(self, L):
        raise NotImplementedError

    def insert(self, i, b):
        self._check_block_size(b)
        self._check_is_binary(b)
        self._check_cache_size
        
        block_addr = self._map_address_to_block(b)
        ret = super(Cache, self).insert(block_addr, x)
        # Dirty flags are handled by child

    def reset(self):
        for i in self.num_cache_lines:
            self[i] = [-1]*self.block_size

    def __add__(self, L):
        raise NotImplementedError

    def __iadd__(self, L):
        raise NotImplementedError

    def __setslice__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, b):
        block_addr = self._map_address_to_block(b)
        return self.__getitem__(self, b)


def MSICache(Cache):

    def __init__(self, *args, **kwargs):
        super(MSICache, self).__init__(self, *args, **kwargs)
        self.state_transitions = {"__getitem__": {"I": "S",
                                                  "S": "S",
                                                  "M": "M"},
                                  "insert": {"I": "M",
                                             "S": "M",
                                             "M": "M"}}
                                  

    def insert(self, i, b):
        super(MSICache, self).insert(i, b)
        self.state_flags[b] = \
            self.state_transitions[method_name][self.state_flags[b]]

    def reset(self):
        super(MSICache, self).reset()
        self.state_flags = ["I"]*self.num_cache_lines

    def __getitem__(self, b):
        method_name = inspect.stack()[0][3]
        self.state_flags[b] = \
            self.state_transitions[method_name][self.state_flags[b]]
        
        return super(MSICache, self).__getitem__(b)

