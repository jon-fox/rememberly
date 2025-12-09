"""Rememberly MCP Server - Context and Chat History Management."""

from fastmcp import FastMCP

from typing import List
from interfaces.tool import Tool
from services.tool_service import ToolService
from tools.example_memory import ExampleMemoryTool
from starlette.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Rememberly",
    instructions="""
    Use this MCP server for managing context and chat history, including:
    - Storing and retrieving conversation context
    - Managing long-term memory across sessions
    - Searching through historical interactions
    - Maintaining user preferences and information

    When a user wants to remember something or recall past conversations, use the MCP tools to provide contextual memory.

    This server provides memory and context management including:
    - Context storage and retrieval
    - Chat history management
    - Semantic search across conversations
    - User preference tracking
    - Session management

    Recommended workflow when managing context:
    1. Use memory tools to store important information from conversations
    2. Retrieve relevant context when needed for continuity
    3. Search historical conversations for specific topics
    4. Maintain user preferences across sessions

    Always provide contextual awareness using these tools rather than relying solely on immediate conversation context.
    """,
)


def get_available_tools() -> List[Tool]:
    """Get list of all available tools."""
    logger.info("Initializing available tools")
    tools = [
        ExampleMemoryTool(),
    ]
    logger.info(f"Successfully initialized {len(tools)} tools")
    return tools


# def get_available_resources() -> List[Resource]:
#     """Get list of all available resources."""
#     return []


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server."""
    logger.info("Creating MCP server instance")
    mcp = FastMCP("example-mcp-server")
    tool_service = ToolService()
    # resource_service = ResourceService()

    # Register all tools and their MCP handlers
    logger.info("Registering tools and MCP handlers")
    tool_service.register_tools(get_available_tools())
    tool_service.register_mcp_handlers(mcp)

    # Register all resources and their MCP handlers
    logger.info("Registering resources and MCP handlers")
    # resource_service.register_resources(get_available_resources())
    # resource_service.register_mcp_handlers(mcp)

    logger.info("MCP server configuration completed successfully")
    return mcp


def create_http_app():
    """Create a FastMCP HTTP app with CORS middleware."""
    mcp_server = create_mcp_server()

    app = mcp_server.http_app()  # type: ignore[attr-defined]

    # Apply CORS middleware manually
    app = CORSMiddleware(
        app,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    return app
