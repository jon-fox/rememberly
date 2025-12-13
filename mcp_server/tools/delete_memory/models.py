"""Models for Delete Memory tool."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class DeleteMemoryInput(BaseToolInput):
    """Input schema for Delete Memory tool."""

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

    key: str = Field(description="The key/identifier for the memory item to delete")
    bucket: str = Field(
        default="default",
        description="The bucket (container) containing the memory. Defaults to 'default'.",
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to organize memories (e.g., user_id, session_id)",
    )


class DeleteMemoryOutput(BaseModel):
    """Output schema for Delete Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "key": "user_preferences",
                    "deleted": True,
                    "message": "Memory 'user_preferences' deleted successfully",
                }
            ]
        }
    )

    success: bool = Field(description="Whether the operation completed successfully")
    key: str = Field(description="The key that was requested for deletion")
    deleted: bool = Field(description="Whether the memory was actually deleted (false if not found)")
    message: str = Field(description="Status message about the operation")
