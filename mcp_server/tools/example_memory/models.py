"""Pydantic models for the Example Memory tool."""

from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from mcp_server.interfaces.tool import BaseToolInput


class ExampleMemoryInput(BaseToolInput):
    """Input schema for Example Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "query": "What did we discuss about the project?",
                }
            ]
        }
    )

    query: str = Field(description="Query to search memory")


class ExampleMemoryOutput(BaseModel):
    """Output schema for Example Memory tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "result": "Placeholder memory response"
                }
            ]
        }
    )

    result: str = Field(
        description="Memory search result"
    )
