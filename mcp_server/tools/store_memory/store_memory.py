"""Tool for storing memories."""

from typing import Dict, Any
from datetime import datetime, timezone
from interfaces.tool import Tool, ToolResponse
from .models import StoreMemoryInput, StoreMemoryOutput
from utils import get_shared_storage


class StoreMemoryTool(Tool):
    """Tool for storing memories and context."""

    name = "store_memory"
    description = (
        "Store a memory item for later retrieval. Use this to remember important "
        "information, context, user preferences, or conversation history. "
        "Supports buckets for organizing memories into collections (e.g., 'real_estate', 'personal') "
        "and optional tags for categorization. Can set TTL for automatic expiration of memories."
    )
    input_model = StoreMemoryInput
    output_model = StoreMemoryOutput

    def __init__(self):
        """Initialize the store memory tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    def _get_storage_key(self, key: str, bucket: str) -> str:
        """Generate a storage key with bucket."""
        return f"{bucket}:{key}"

    async def execute(self, input_data: StoreMemoryInput) -> ToolResponse:
        """Execute the store memory tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response confirming the memory was stored
        """
        storage_key = self._get_storage_key(input_data.key, input_data.bucket)
        now = datetime.now(timezone.utc)

        # Store the memory with metadata
        memory_data = {
            "value": input_data.value,
            "metadata": {
                "stored_at": now.isoformat(),
                "bucket": input_data.bucket,
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

        output = StoreMemoryOutput(
            success=True,
            key=input_data.key,
            message=f"Memory stored successfully under key '{input_data.key}'",
            metadata=memory_data["metadata"],
        )

        return ToolResponse.from_model(output)
