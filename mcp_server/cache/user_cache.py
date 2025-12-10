"""User data caching with TTL support."""

import time
from typing import Optional, Dict, Any
from threading import Lock

_cache: Dict[str, Dict[str, Any]] = {}
_lock = Lock()
_ttl_seconds = 3600


def get(user_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        if user_id not in _cache:
            return None

        entry = _cache[user_id]
        if time.time() > entry["_expiry"]:
            del _cache[user_id]
            return None

        return entry["data"]


def set(user_id: str, user_data: Dict[str, Any]) -> None:
    with _lock:
        _cache[user_id] = {"data": user_data, "_expiry": time.time() + _ttl_seconds}
