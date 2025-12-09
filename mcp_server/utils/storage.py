"""Shared storage for memory tools."""

from typing import Dict, Any


class MemoryStorage:
    """Shared in-memory storage for memory tools.
    
    In production, this would be replaced with a database or cache service.
    This class ensures that GetMemoryTool, PutMemoryTool, and ListMemoriesTool share the same storage.
    """

    def __init__(self):
        """Initialize the storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Dict[str, Any] | None:
        """Get a memory item by key."""
        return self._storage.get(key)

    def put(self, key: str, value: Dict[str, Any]) -> None:
        """Store a memory item."""
        self._storage[key] = value

    def has(self, key: str) -> bool:
        """Check if a key exists."""
        return key in self._storage

    def delete(self, key: str) -> bool:
        """Delete a memory item by key."""
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all memory items."""
        self._storage.clear()
    
    def keys(self) -> list[str]:
        """Get all storage keys."""
        return list(self._storage.keys())


# Global storage instance shared by all memory tools
_shared_storage = MemoryStorage()


def get_shared_storage() -> MemoryStorage:
    """Get the shared memory storage instance."""
    return _shared_storage
