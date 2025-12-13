"""Models for Create Bucket tool."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class CreateBucketInput(BaseToolInput):
    """Input schema for Create Bucket tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "real_estate",
                },
                {
                    "name": "work_projects",
                    "description": "Memories related to work projects and tasks",
                },
            ]
        }
    )

    name: str = Field(
        description="The name of the bucket to create (use lowercase and underscores)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of what this bucket is for",
    )


class CreateBucketOutput(BaseModel):
    """Output schema for Create Bucket tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "bucket_name": "real_estate",
                    "message": "Bucket 'real_estate' created successfully",
                }
            ]
        }
    )

    success: bool = Field(description="Whether the bucket was created successfully")
    bucket_name: str = Field(description="The name of the created bucket")
    message: str = Field(description="Success or error message")
