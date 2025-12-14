"""Models for Get Metrics tool."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class GetMetricsInput(BaseToolInput):
    """Input schema for Get Metrics tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {},
                {
                    "bucket": "real_estate",
                },
                {
                    "include_memory_details": True,
                },
            ]
        }
    )

    bucket: Optional[str] = Field(
        default=None,
        description="Optional bucket to get detailed metrics for. If not provided, returns overall metrics.",
    )
    include_memory_details: bool = Field(
        default=False,
        description="If true, include detailed information about each memory (size, timestamps, etc.)",
    )


class BucketMetrics(BaseModel):
    """Metrics for a single bucket."""

    name: str = Field(description="Bucket name")
    memory_count: int = Field(description="Number of memories in the bucket")
    total_size_bytes: int = Field(description="Total size of all memories in bytes")
    oldest_memory_timestamp: Optional[str] = Field(
        default=None, description="Timestamp of the oldest memory"
    )
    newest_memory_timestamp: Optional[str] = Field(
        default=None, description="Timestamp of the newest memory"
    )


class MemoryDetail(BaseModel):
    """Detailed information about a single memory."""

    key: str = Field(description="Memory key")
    bucket: str = Field(description="Bucket name")
    size_bytes: int = Field(description="Size of the memory value in bytes")
    stored_at: Optional[str] = Field(
        default=None, description="When the memory was stored"
    )
    has_ttl: bool = Field(description="Whether the memory has a TTL set")
    expires_at: Optional[str] = Field(
        default=None, description="When the memory expires (if TTL is set)"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags associated with the memory"
    )


class GetMetricsOutput(BaseModel):
    """Output schema for Get Metrics tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_buckets": 3,
                    "total_memories": 25,
                    "total_size_bytes": 15360,
                    "bucket_metrics": [
                        {
                            "name": "default",
                            "memory_count": 10,
                            "total_size_bytes": 5120,
                            "oldest_memory_timestamp": "2025-12-08T10:00:00Z",
                            "newest_memory_timestamp": "2025-12-12T15:30:00Z",
                        }
                    ],
                }
            ]
        }
    )

    total_buckets: int = Field(description="Total number of buckets")
    total_memories: int = Field(description="Total number of memories across all buckets")
    total_size_bytes: int = Field(description="Total size of all memories in bytes")
    bucket_metrics: List[BucketMetrics] = Field(
        description="Metrics for each bucket (or single bucket if filtered)"
    )
    memory_details: Optional[List[MemoryDetail]] = Field(
        default=None,
        description="Detailed information about each memory (if include_memory_details=true)",
    )

