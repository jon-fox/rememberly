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
                    "key": "property_listing",
                    "bucket": "real_estate",
                },
            ]
        }
    )

    key: str = Field(description="The key/identifier for the memory item to delete")
    bucket: str = Field(
        default="default",
        description="The bucket (container) containing the memory. Defaults to 'default'.",
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
    deleted: bool = Field(
        description="Whether the memory was actually deleted (false if not found)"
    )
    message: str = Field(description="Status message about the operation")
