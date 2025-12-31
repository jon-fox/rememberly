"""Tool for deleting memories."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import DeleteMemoryInput, DeleteMemoryOutput
from utils import get_shared_storage


class DeleteMemoryTool(Tool):
    """Tool for deleting stored memories."""

    name = "delete_memory"
    description = (
        "Delete a stored memory item by key. Use this to remove information "
        "that is no longer needed or should be forgotten. Supports buckets "
        "to organize the memory to delete."
    )
    input_model = DeleteMemoryInput
    output_model = DeleteMemoryOutput

    def __init__(self):
        """Initialize the delete memory tool."""
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

    async def execute(self, input_data: DeleteMemoryInput) -> ToolResponse:
        """Execute the delete memory tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response confirming whether the memory was deleted
        """
        storage_key = self._get_storage_key(input_data.key, input_data.bucket)

        deleted = self._storage.delete(storage_key)

        if deleted:
            output = DeleteMemoryOutput(
                success=True,
                key=input_data.key,
                deleted=True,
                message=f"Memory '{input_data.key}' deleted successfully",
            )
        else:
            output = DeleteMemoryOutput(
                success=True,
                key=input_data.key,
                deleted=False,
                message=f"Memory '{input_data.key}' not found",
            )

        return ToolResponse.from_model(output)
