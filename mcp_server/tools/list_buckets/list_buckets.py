"""Tool for listing all buckets."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import ListBucketsInput, ListBucketsOutput, BucketInfo
from utils import get_shared_storage
from services.tool_service import get_user_email


class ListBucketsTool(Tool):
    """Tool for listing all available buckets."""

    name = "list_buckets"
    description = (
        "List all available buckets (containers for organizing memories). "
        "Buckets allow you to organize memories into separate collections, "
        "such as 'real_estate', 'personal', 'work', etc. Shows the bucket names "
        "and the number of memories in each bucket."
    )
    input_model = ListBucketsInput
    output_model = ListBucketsOutput

    def __init__(self):
        """Initialize the list buckets tool."""
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

    async def execute(self, input_data: ListBucketsInput) -> ToolResponse:
        """Execute the list buckets tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing the list of buckets
        """
        user_email = get_user_email()
        all_keys = self._storage.keys_for_user(user_email)

        # Count memories per bucket
        bucket_counts: Dict[str, int] = {}
        for storage_key in all_keys:
            user_email, bucket, key = self._parse_storage_key(storage_key)
            # Skip bucket metadata entries when counting
            if key.startswith("__bucket_meta__"):
                continue
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        # Build bucket info list
        buckets = [
            BucketInfo(name=bucket, memory_count=count)
            for bucket, count in sorted(bucket_counts.items())
        ]

        output = ListBucketsOutput(
            buckets=buckets,
            total_buckets=len(buckets),
        )

        return ToolResponse.from_model(output)
