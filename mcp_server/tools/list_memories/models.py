"""Models for List Memories tool."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class ListMemoriesInput(BaseToolInput):
    """Input schema for List Memories tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {},
                {
                    "namespace": "session_123",
                },
                {
                    "prefix": "user_",
                },
                {
                    "bucket": "real_estate",
                },
            ]
        }
    )

    bucket: Optional[str] = Field(
        default=None,
        description="Optional bucket filter to list memories from a specific bucket. If not provided, lists from all buckets.",
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace filter to list memories from a specific namespace",
    )
    prefix: Optional[str] = Field(
        default=None,
        description="Optional key prefix filter to list memories with keys starting with this prefix",
    )


class MemoryItem(BaseModel):
    """Single memory item in the list."""

    key: str = Field(description="The memory key")
    bucket: str = Field(description="The bucket the memory belongs to")
    namespace: str = Field(description="The namespace the memory belongs to")
    has_value: bool = Field(description="Whether the memory has a stored value")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata about the memory"
    )


class ListMemoriesOutput(BaseModel):
    """Output schema for List Memories tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "memories": [
                        {
                            "key": "user_preferences",
                            "namespace": "default",
                            "has_value": True,
                            "metadata": {"created_at": "2025-12-08T10:00:00Z"},
                        },
                        {
                            "key": "conversation_context",
                            "namespace": "session_123",
                            "has_value": True,
                            "metadata": {"created_at": "2025-12-08T11:00:00Z"},
                        },
                    ],
                    "count": 2,
                    "namespace_filter": None,
                    "prefix_filter": None,
                }
            ]
        }
    )

    memories: List[MemoryItem] = Field(description="List of memory items")
    count: int = Field(description="Total number of memories returned")
    namespace_filter: Optional[str] = Field(
        default=None, description="The namespace filter that was applied, if any"
    )
    prefix_filter: Optional[str] = Field(
        default=None, description="The prefix filter that was applied, if any"
    )
