"""Tool for getting storage metrics."""

from typing import Dict, Any, List
import sys
from datetime import datetime
from interfaces.tool import Tool, ToolResponse
from .models import GetMetricsInput, GetMetricsOutput, BucketMetrics, MemoryDetail
from utils import get_shared_storage
from services.tool_service import get_user_email


class GetMetricsTool(Tool):
    """Tool for getting storage metrics and statistics."""

    name = "get_metrics"
    description = (
        "Get detailed metrics about memory storage including bucket counts, "
        "memory counts, storage sizes, and timestamps. Can provide overall metrics "
        "or detailed metrics for a specific bucket. Useful for understanding storage "
        "usage and finding information about stored memories."
    )
    input_model = GetMetricsInput
    output_model = GetMetricsOutput

    def __init__(self):
        """Initialize the get metrics tool."""
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

    def _get_value_size(self, value: Any) -> int:
        """Get the approximate size of a value in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, (dict, list)):
                return sys.getsizeof(str(value))
            else:
                return sys.getsizeof(value)
        except:
            return 0

    async def execute(self, input_data: GetMetricsInput) -> ToolResponse:
        """Execute the get metrics tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing storage metrics
        """
        user_email = get_user_email()
        all_keys = self._storage.keys_for_user(user_email)

        # Organize data by bucket
        bucket_data: Dict[str, List[tuple[str, Any]]] = {}

        for storage_key in all_keys:
            user_email, bucket, key = self._parse_storage_key(storage_key)

            # Skip bucket metadata entries
            if key.startswith("__bucket_meta__"):
                continue

            # Filter by bucket if specified
            if input_data.bucket and bucket != input_data.bucket:
                continue

            stored_data = self._storage.get(storage_key)

            if bucket not in bucket_data:
                bucket_data[bucket] = []

            bucket_data[bucket].append((key, stored_data))

        # Calculate metrics for each bucket
        bucket_metrics_list: List[BucketMetrics] = []
        memory_details_list: List[MemoryDetail] = []
        total_memories = 0
        total_size_bytes = 0

        for bucket, memories in sorted(bucket_data.items()):
            bucket_size = 0
            oldest_timestamp = None
            newest_timestamp = None

            for key, stored_data in memories:
                total_memories += 1

                # Get value and calculate size
                value = (
                    stored_data.get("value")
                    if isinstance(stored_data, dict)
                    else stored_data
                )
                size = self._get_value_size(value)
                bucket_size += size
                total_size_bytes += size

                # Track timestamps
                if isinstance(stored_data, dict) and "metadata" in stored_data:
                    metadata = stored_data["metadata"]
                    stored_at = metadata.get("stored_at")

                    if stored_at:
                        if oldest_timestamp is None or stored_at < oldest_timestamp:
                            oldest_timestamp = stored_at
                        if newest_timestamp is None or stored_at > newest_timestamp:
                            newest_timestamp = stored_at

                    # Add memory details if requested
                    if input_data.include_memory_details:
                        memory_detail = MemoryDetail(
                            key=key,
                            bucket=bucket,
                            size_bytes=size,
                            stored_at=stored_at,
                            has_ttl=metadata.get("ttl") is not None,
                            expires_at=metadata.get("expires_at"),
                            tags=metadata.get("tags"),
                        )
                        memory_details_list.append(memory_detail)

            bucket_metrics = BucketMetrics(
                name=bucket,
                memory_count=len(memories),
                total_size_bytes=bucket_size,
                oldest_memory_timestamp=oldest_timestamp,
                newest_memory_timestamp=newest_timestamp,
            )
            bucket_metrics_list.append(bucket_metrics)

        output = GetMetricsOutput(
            total_buckets=len(bucket_metrics_list),
            total_memories=total_memories,
            total_size_bytes=total_size_bytes,
            bucket_metrics=bucket_metrics_list,
            memory_details=(
                memory_details_list if input_data.include_memory_details else None
            ),
        )

        return ToolResponse.from_model(output)
