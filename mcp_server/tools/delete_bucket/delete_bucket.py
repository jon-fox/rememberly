"""Tool for deleting a bucket."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import DeleteBucketInput, DeleteBucketOutput
from utils import get_shared_storage
from services.tool_service import get_user_email


class DeleteBucketTool(Tool):
    """Tool for deleting a bucket and optionally all its memories."""

    name = "delete_bucket"
    description = (
        "Delete a bucket (container) and optionally all memories within it. "
        "By default, only empty buckets can be deleted. Set force=true to "
        "delete a bucket with all its memories. This operation cannot be undone."
    )
    input_model = DeleteBucketInput
    output_model = DeleteBucketOutput

    def __init__(self):
        """Initialize the delete bucket tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    def _parse_storage_key(self, storage_key: str) -> tuple[str, str, str]:
        """Parse a storage key into user_email, bucket and key.

        Format: {user_email}/{bucket}/{key}
        """
        parts = storage_key.split("/", 2)
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            return "unknown", parts[0], parts[1]
        return "unknown", "default", storage_key

    async def execute(self, input_data: DeleteBucketInput) -> ToolResponse:
        """Execute the delete bucket tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response confirming whether the bucket was deleted
        """
        user_email = get_user_email()
        bucket_name = input_data.name.lower().strip()

        # Prevent deletion of default bucket
        if bucket_name == "default":
            output = DeleteBucketOutput(
                success=False,
                bucket_name=bucket_name,
                deleted=False,
                memories_deleted=0,
                message="Cannot delete the 'default' bucket",
            )
            return ToolResponse.from_model(output)

        # Find all keys in this bucket for this user
        all_keys = self._storage.keys_for_user(user_email)
        bucket_keys = [
            key for key in all_keys if self._parse_storage_key(key)[1] == bucket_name
        ]

        # Check if bucket exists
        if not bucket_keys:
            output = DeleteBucketOutput(
                success=True,
                bucket_name=bucket_name,
                deleted=False,
                memories_deleted=0,
                message=f"Bucket '{bucket_name}' not found",
            )
            return ToolResponse.from_model(output)

        # Count non-metadata memories
        memory_keys = [key for key in bucket_keys if "__bucket_meta__" not in key]

        # Check if bucket has memories and force is not set
        if memory_keys and not input_data.force:
            output = DeleteBucketOutput(
                success=False,
                bucket_name=bucket_name,
                deleted=False,
                memories_deleted=0,
                message=f"Bucket '{bucket_name}' contains {len(memory_keys)} memories. Use force=true to delete.",
            )
            return ToolResponse.from_model(output)

        # Delete all keys in the bucket
        deleted_count = 0
        for key in bucket_keys:
            if self._storage.delete(key):
                deleted_count += 1

        memories_deleted = len([k for k in bucket_keys if "__bucket_meta__" not in k])

        output = DeleteBucketOutput(
            success=True,
            bucket_name=bucket_name,
            deleted=True,
            memories_deleted=memories_deleted,
            message=f"Bucket '{bucket_name}' and {memories_deleted} memories deleted successfully",
        )

        return ToolResponse.from_model(output)
