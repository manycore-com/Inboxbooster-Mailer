from collections import OrderedDict
import logging


class LRUCache:

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str, default=None):
        if key not in self.cache:
            return default
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value) -> None:
        #logging.info("lrucache: put " + str(key) + " " + str(value))
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
