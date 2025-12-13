"""Models for Put Memory tool."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class PutMemoryInput(BaseToolInput):
    """Input schema for Put Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "key": "user_preferences",
                    "value": {"theme": "dark", "language": "en"},
                },
                {
                    "key": "conversation_summary",
                    "value": "User asked about MCP resources and datetime handling",
                    "namespace": "session_123",
                    "tags": ["conversation", "mcp", "datetime"],
                },
                {
                    "key": "property_123",
                    "value": {"address": "123 Main St", "price": 500000},
                    "bucket": "real_estate",
                    "tags": ["listing", "for_sale"],
                },
            ]
        }
    )

    key: str = Field(description="The key/identifier for storing the memory item")
    value: Any = Field(
        description="The value to store (can be string, dict, list, etc.)"
    )
    bucket: str = Field(
        default="default",
        description="The bucket (container) to store the memory in. Defaults to 'default'.",
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to organize memories (e.g., user_id, session_id)",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Optional tags for categorizing and searching memories",
    )
    ttl: Optional[int] = Field(
        default=None,
        description="Optional time-to-live in seconds (for expiring memories)",
    )


class PutMemoryOutput(BaseModel):
    """Output schema for Put Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "key": "user_preferences",
                    "message": "Memory stored successfully",
                    "metadata": {
                        "stored_at": "2025-12-08T10:00:00Z",
                        "namespace": "default",
                    },
                }
            ]
        }
    )

    success: bool = Field(description="Whether the memory was stored successfully")
    key: str = Field(description="The key that was stored")
    message: str = Field(description="Status message about the operation")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadata about the stored memory"
    )
