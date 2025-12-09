"""Tool for listing all stored memories."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import ListMemoriesInput, ListMemoriesOutput, MemoryItem
from utils import get_shared_storage


class ListMemoriesTool(Tool):
    """Tool for listing all stored memories with optional filtering."""

    name = "list_memories"
    description = (
        "List all stored memories with optional filtering by namespace or key prefix. "
        "Use this to discover what information has been stored, to find specific "
        "memories, or to get an overview of available context. Supports filtering "
        "by namespace (e.g., user_id, session_id) or key prefix."
    )
    input_model = ListMemoriesInput
    output_model = ListMemoriesOutput

    def __init__(self):
        """Initialize the list memories tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    def _parse_storage_key(self, storage_key: str) -> tuple[str, str]:
        """Parse a storage key into namespace and key."""
        if ":" in storage_key:
            namespace, key = storage_key.split(":", 1)
            return namespace, key
        return "default", storage_key

    def _matches_filters(
        self, namespace: str, key: str, namespace_filter: str | None, prefix_filter: str | None
    ) -> bool:
        """Check if a memory item matches the given filters."""
        if namespace_filter and namespace != namespace_filter:
            return False
        if prefix_filter and not key.startswith(prefix_filter):
            return False
        return True

    async def execute(self, input_data: ListMemoriesInput) -> ToolResponse:
        """Execute the list memories tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing the list of memory items
        """
        # Get all storage keys using the public method
        all_keys = self._storage.keys()

        # Filter and build memory items
        memory_items = []
        for storage_key in all_keys:
            namespace, key = self._parse_storage_key(storage_key)

            # Apply filters
            if not self._matches_filters(
                namespace, key, input_data.namespace, input_data.prefix
            ):
                continue

            # Get the stored data
            stored_data = self._storage.get(storage_key)
            has_value = stored_data is not None

            # Extract metadata if available
            metadata = None
            if stored_data and isinstance(stored_data, dict):
                metadata = stored_data.get("metadata")

            memory_items.append(
                MemoryItem(
                    key=key,
                    namespace=namespace,
                    has_value=has_value,
                    metadata=metadata,
                )
            )

        # Create output
        output = ListMemoriesOutput(
            memories=memory_items,
            count=len(memory_items),
            namespace_filter=input_data.namespace,
            prefix_filter=input_data.prefix,
        )

        return ToolResponse(
            success=True,
            result=output.model_dump(),
            error=None,
        )
