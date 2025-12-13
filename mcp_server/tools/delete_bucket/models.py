"""Models for Delete Bucket tool."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class DeleteBucketInput(BaseToolInput):
    """Input schema for Delete Bucket tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "real_estate",
                },
                {
                    "name": "old_project",
                    "force": True,
                },
            ]
        }
    )

    name: str = Field(
        description="The name of the bucket to delete"
    )
    force: bool = Field(
        default=False,
        description="If true, delete the bucket even if it contains memories. If false, only delete empty buckets.",
    )


class DeleteBucketOutput(BaseModel):
    """Output schema for Delete Bucket tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "bucket_name": "real_estate",
                    "deleted": True,
                    "memories_deleted": 5,
                    "message": "Bucket 'real_estate' and 5 memories deleted successfully",
                }
            ]
        }
    )

    success: bool = Field(description="Whether the operation completed successfully")
    bucket_name: str = Field(description="The name of the bucket")
    deleted: bool = Field(description="Whether the bucket was actually deleted")
    memories_deleted: int = Field(description="Number of memories that were deleted with the bucket")
    message: str = Field(description="Status message about the operation")
