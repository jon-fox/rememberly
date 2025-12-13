"""Models for List Buckets tool."""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from interfaces.tool import BaseToolInput


class ListBucketsInput(BaseToolInput):
    """Input schema for List Buckets tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {},
            ]
        }
    )


class BucketInfo(BaseModel):
    """Information about a single bucket."""

    name: str = Field(description="The name of the bucket")
    memory_count: int = Field(description="Number of memories in this bucket")


class ListBucketsOutput(BaseModel):
    """Output schema for List Buckets tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "buckets": [
                        {"name": "default", "memory_count": 5},
                        {"name": "real_estate", "memory_count": 12},
                    ],
                    "total_buckets": 2,
                }
            ]
        }
    )

    buckets: List[BucketInfo] = Field(description="List of available buckets")
    total_buckets: int = Field(description="Total number of buckets")
