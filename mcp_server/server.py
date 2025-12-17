"""Rememberly MCP Server - Context and Chat History Management."""

from fastmcp import FastMCP

from typing import List
from interfaces.tool import Tool
from interfaces.resource import Resource
from services.tool_service import ToolService
from services.resource_service import ResourceService
from tools import GetMemoryTool, StoreMemoryTool, DeleteMemoryTool, ListMemoriesTool, ListBucketsTool, CreateBucketTool, DeleteBucketTool, GetMetricsTool
from resources import DateTimeResource
from starlette.middleware.cors import CORSMiddleware
from middleware import AuthMiddleware
from auth import get_jwt_verifier
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
        GetMemoryTool(),
        StoreMemoryTool(),
        DeleteMemoryTool(),
        ListMemoriesTool(),
        ListBucketsTool(),
        CreateBucketTool(),
        DeleteBucketTool(),
        GetMetricsTool(),
    ]
    logger.info(f"Successfully initialized {len(tools)} tools")
    return tools


def get_available_resources() -> List[Resource]:
    """Get list of all available resources."""
    logger.info("Initializing available resources")
    resources = [
        DateTimeResource(),
    ]
    logger.info(f"Successfully initialized {len(resources)} resources")
    return resources


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server."""
    logger.info("Creating MCP server instance")
    
    # Enable stateless_http for Lambda deployment with JWT auth
    mcp = FastMCP("example-mcp-server", stateless_http=True, auth=get_jwt_verifier())
    tool_service = ToolService()
    resource_service = ResourceService()

    # Register all tools and their MCP handlers
    logger.info("Registering tools and MCP handlers")
    tool_service.register_tools(get_available_tools())
    tool_service.register_mcp_handlers(mcp)

    # Register all resources and their MCP handlers
    logger.info("Registering resources and MCP handlers")
    resource_service.register_resources(get_available_resources())
    resource_service.register_mcp_handlers(mcp)

    logger.info("MCP server configuration completed successfully")
    return mcp


def create_http_app():
    """Create a FastMCP HTTP app with CORS and Auth middleware."""
    mcp_server = create_mcp_server()

    app = mcp_server.http_app()  # type: ignore[attr-defined]
    app.add_middleware(AuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    return app


# Export app for uvicorn (used by Lambda Web Adapter)
app = create_http_app()
