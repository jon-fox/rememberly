"""Tool for storing memories."""

from typing import Dict, Any
from datetime import datetime, timezone
from interfaces.tool import Tool, ToolResponse
from .models import PutMemoryInput, PutMemoryOutput
from utils import get_shared_storage


class PutMemoryTool(Tool):
    """Tool for storing memories and context."""

    name = "put_memory"
    description = (
        "Store a memory item for later retrieval. Use this to remember important "
        "information, context, user preferences, or conversation history. "
        "Supports namespaces for organizing memories and optional tags for categorization. "
        "Can set TTL for automatic expiration of memories."
    )
    input_model = PutMemoryInput
    output_model = PutMemoryOutput

    def __init__(self):
        """Initialize the put memory tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    def _get_storage_key(self, key: str, namespace: str | None) -> str:
        """Generate a storage key with namespace."""
        if namespace:
            return f"{namespace}:{key}"
        return f"default:{key}"

    async def execute(self, input_data: PutMemoryInput) -> ToolResponse:
        """Execute the put memory tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response confirming the memory was stored
        """
        storage_key = self._get_storage_key(input_data.key, input_data.namespace)
        now = datetime.now(timezone.utc)

        # Store the memory with metadata
        memory_data = {
            "value": input_data.value,
            "metadata": {
                "stored_at": now.isoformat(),
                "namespace": input_data.namespace or "default",
                "key": input_data.key,
            },
        }

        # Add optional fields to metadata
        if input_data.tags:
            memory_data["metadata"]["tags"] = input_data.tags

        if input_data.ttl:
            memory_data["metadata"]["ttl"] = input_data.ttl
            memory_data["metadata"]["expires_at"] = now.timestamp() + input_data.ttl

        self._storage.put(storage_key, memory_data)

        output = PutMemoryOutput(
            success=True,
            key=input_data.key,
            message=f"Memory stored successfully under key '{input_data.key}'",
            metadata=memory_data["metadata"],
        )

        return ToolResponse.from_model(output)
