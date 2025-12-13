"""Models for Get Memory tool."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class GetMemoryInput(BaseToolInput):
    """Input schema for Get Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "key": "user_preferences",
                },
                {
                    "key": "conversation_context",
                    "namespace": "session_123",
                },
                {
                    "key": "property_listing",
                    "bucket": "real_estate",
                    "namespace": "session_123",
                },
            ]
        }
    )

    key: str = Field(description="The key/identifier for the memory item to retrieve")
    bucket: str = Field(
        default="default",
        description="The bucket (container) to retrieve the memory from. Defaults to 'default'.",
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to organize memories (e.g., user_id, session_id)",
    )


class GetMemoryOutput(BaseModel):
    """Output schema for Get Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "key": "user_preferences",
                    "value": {"theme": "dark", "language": "en"},
                    "found": True,
                    "metadata": {"created_at": "2025-12-08T10:00:00Z"},
                }
            ]
        }
    )

    key: str = Field(description="The key that was requested")
    value: Optional[Any] = Field(
        default=None, description="The stored value, or None if not found"
    )
    found: bool = Field(description="Whether the memory item was found")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the memory (timestamps, etc.)",
    )
