from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class _Entry(Generic[V]):
    value: V
    expires_at: float


class InMemoryTTLCache(Generic[K, V]):
    """
    Simple thread-safe Time To Live cache with Least Recently Used eviction.

    - TTL is per-item (same ttl_seconds for all entries)
    - LRU eviction when maxsize exceeded
    - Per-process (not shared across workers / pods)
    """

    def __init__(self, *, maxsize: int = 50_000, ttl_seconds: float = 300.0) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be > 0")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")

        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._lock = RLock()
        self._data: OrderedDict[K, _Entry[V]] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                self._data.pop(key, None)
                return None

            # mark as recently used
            self._data.move_to_end(key, last=True)
            return entry.value

    def set(self, key: K, value: V) -> None:
        now = time.time()
        with self._lock:
            self._data[key] = _Entry(value=value, expires_at=now + self._ttl)
            self._data.move_to_end(key, last=True)

            # evict LRU
            while len(self._data) > self._maxsize:
                self._data.popitem(last=False)
