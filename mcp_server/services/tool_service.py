"""Service layer for managing tools."""

from typing import Dict, List, Any
from functools import wraps
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from interfaces.tool import Tool, ToolResponse, ToolContent
import logging


logger = logging.getLogger(__name__)


def get_user_email() -> str:
    """Get the current user's email from the access token."""
    token = get_access_token()
    return token.claims.get("email")


def get_user_id() -> str:
    """Get the current user's ID (sub) from the access token."""
    token = get_access_token()
    return token.claims.get("sub")


def require_auth(func):
    """Decorator for logging tool execution.

    Note: With FastMCP GoogleProvider, authentication is enforced at the server level.
    If a request reaches the tool, the user is already authenticated.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            user_email = get_user_email()
            user_id = get_user_id()
            logger.info(
                f"Tool call: {func.__name__} | User: {user_email} (ID: {user_id})"
            )
        except Exception as e:
            logger.warning(f"Could not extract user info: {str(e)}")

        result = await func(*args, **kwargs)
        logger.info(f"Tool {func.__name__} completed")
        return result

    return wrapper


class ToolService:
    """Service for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool

    def register_tools(self, tools: List[Tool]) -> None:
        """Register multiple tools."""
        for tool in tools:
            self.register_tool(tool)

    def get_tool(self, tool_name: str) -> Tool:
        """Get a tool by name."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool not found: {tool_name}")
        return self._tools[tool_name]

    async def execute_tool(
        self, tool_name: str, input_data: Dict[str, Any]
    ) -> ToolResponse:
        """Execute a tool by name with given arguments.

        Args:
            tool_name: The name of the tool to execute
            input_data: Dictionary of input arguments for the tool

        Returns:
            The tool's response containing the execution results

        Raises:
            ValueError: If the tool is not found
            ValidationError: If the input data is invalid
        """
        tool = self.get_tool(tool_name)

        # Use model_validate to handle complex nested objects properly
        input_model = tool.input_model.model_validate(input_data)

        # Execute the tool with validated input
        result = await tool.execute(input_model)
        return result

    def _process_tool_content(self, content: ToolContent) -> Any:
        """Process a ToolContent object based on its type.

        Args:
            content: The ToolContent to process

        Returns:
            The appropriate representation of the content based on its type
        """
        if content.type == "text":
            return content.text
        elif content.type == "json" and content.json_data is not None:
            return content.json_data
        else:
            # Default to returning whatever is available
            return content.text or content.json_data or {}

    def _serialize_response(self, response: ToolResponse) -> Any:
        """Serialize a ToolResponse to return to the client.

        This handles the actual response serialization based on content types.

        Args:
            response: The ToolResponse to serialize

        Returns:
            The serialized response
        """
        if not response.content:
            return {}

        # If there's only one content item, return it directly
        if len(response.content) == 1:
            return self._process_tool_content(response.content[0])

        # If there are multiple content items, return them as a list
        return [self._process_tool_content(content) for content in response.content]

    def register_mcp_handlers(self, mcp: FastMCP) -> None:
        """Register all tools as MCP handlers."""
        for tool in self._tools.values():

            def create_handler(tool_instance):
                @require_auth
                async def handler(input_data: tool_instance.input_model):
                    f'"""{tool_instance.description}"""'
                    result = await self.execute_tool(
                        tool_instance.name, input_data.model_dump()
                    )
                    return self._serialize_response(result)

                return handler

            handler = create_handler(tool)
            mcp.tool(name=tool.name, description=tool.description)(handler)
