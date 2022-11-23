from typing import Optional
import redis


class ReliableQueue:

    # For first version, just assume local redis
    def __init__(self, queue_name: str):
        self._queue_name = queue_name
        self._redis = redis.Redis()

    def push(self, data: bytes):
        self._redis.rpush(self._queue_name, data)

    def blocking_pop(self, timeout=0) -> Optional[bytes]:
        self._redis.blpop(self._queue_name, timeout)

