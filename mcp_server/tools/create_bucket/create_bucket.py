"""Tool for creating a new bucket."""

from typing import Dict, Any
from interfaces.tool import Tool, ToolResponse
from .models import CreateBucketInput, CreateBucketOutput
from utils import get_shared_storage


class CreateBucketTool(Tool):
    """Tool for creating a new bucket to organize memories."""

    name = "create_bucket"
    description = (
        "Create a new bucket (container) for organizing memories. "
        "Buckets allow you to separate memories into different collections, "
        "such as 'real_estate', 'personal', 'work', etc. Each bucket acts as "
        "a separate namespace for memories. The bucket name should use lowercase "
        "letters and underscores (e.g., 'real_estate', 'personal_notes')."
    )
    input_model = CreateBucketInput
    output_model = CreateBucketOutput

    def __init__(self):
        """Initialize the create bucket tool."""
        self._storage = get_shared_storage()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: CreateBucketInput) -> ToolResponse:
        """Execute the create bucket tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response confirming the bucket was created
        """
        bucket_name = input_data.name.lower().strip()

        # Validate bucket name
        if not bucket_name:
            output = CreateBucketOutput(
                success=False,
                bucket_name=bucket_name,
                message="Bucket name cannot be empty",
            )
            return ToolResponse.from_model(output)

        # Check if bucket already exists by looking for any keys with this bucket
        all_keys = self._storage.keys()
        bucket_exists = any(key.startswith(f"{bucket_name}:") for key in all_keys)

        if bucket_exists:
            output = CreateBucketOutput(
                success=True,
                bucket_name=bucket_name,
                message=f"Bucket '{bucket_name}' already exists",
            )
        else:
            # Create a metadata entry for the bucket
            # This ensures the bucket shows up even with no memories
            bucket_meta_key = f"{bucket_name}:__bucket_meta__info"
            self._storage.put(
                bucket_meta_key,
                {
                    "bucket_name": bucket_name,
                    "description": input_data.description or "",
                    "created": True,
                },
            )

            output = CreateBucketOutput(
                success=True,
                bucket_name=bucket_name,
                message=f"Bucket '{bucket_name}' created successfully",
            )

        return ToolResponse.from_model(output)
