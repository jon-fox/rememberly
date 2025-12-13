"""Tool for retrieving memories from storage."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import GetMemoryInput, GetMemoryOutput
from utils import get_shared_storage


class GetMemoryTool(Tool):
    """Tool for retrieving stored memories and context."""

    name = "get_memory"
    description = (
        "Retrieve a stored memory item by key. Use this to recall information, "
        "context, preferences, or conversation history that was previously stored. "
        "Supports buckets for organizing memories into collections (e.g., 'real_estate', 'personal') "
        "and namespaces for organizing memories by user, session, or other categories."
    )
    input_model = GetMemoryInput
    output_model = GetMemoryOutput

    def __init__(self):
        """Initialize the get memory tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    def _get_storage_key(self, key: str, bucket: str, namespace: str | None) -> str:
        """Generate a storage key with bucket and namespace."""
        if namespace:
            return f"{bucket}:{namespace}:{key}"
        return f"{bucket}:default:{key}"

    async def execute(self, input_data: GetMemoryInput) -> ToolResponse:
        """Execute the get memory tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing the retrieved memory or indication it wasn't found
        """
        storage_key = self._get_storage_key(input_data.key, input_data.bucket, input_data.namespace)

        if self._storage.has(storage_key):
            memory_data = self._storage.get(storage_key)
            output = GetMemoryOutput(
                key=input_data.key,
                value=memory_data.get("value"),
                found=True,
                metadata=memory_data.get("metadata", {}),
            )
        else:
            output = GetMemoryOutput(
                key=input_data.key,
                value=None,
                found=False,
                metadata=None,
            )

        return ToolResponse.from_model(output)
