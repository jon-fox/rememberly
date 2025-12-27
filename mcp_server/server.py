"""Rememberly MCP Server - Context and Chat History Management."""

import logging
from typing import List

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from auth import get_supabase_auth
from interfaces.resource import Resource
from interfaces.tool import Tool
from middleware import AuthMiddleware
from resources import DateTimeResource
from services.resource_service import ResourceService
from services.tool_service import ToolService
from tools import (
    CreateBucketTool,
    DeleteBucketTool,
    DeleteMemoryTool,
    GetMemoryTool,
    GetMetricsTool,
    ListBucketsTool,
    ListMemoriesTool,
    StoreMemoryTool,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MCP_INSTRUCTIONS = """
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
    """


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

    mcp = FastMCP(
        "Rememberly",
        auth=get_supabase_auth(),
        instructions=MCP_INSTRUCTIONS,
    )
    
    # Add middleware to MCP server
    logger.info("Adding authentication middleware")
    mcp.add_middleware(AuthMiddleware())
    
    tool_service = ToolService()
    resource_service = ResourceService()

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
    from starlette.applications import Starlette
    from starlette.routing import Mount

    mcp_server = create_mcp_server()
    auth = get_supabase_auth()

    # Get well-known OAuth discovery routes
    well_known_routes = auth.get_well_known_routes(mcp_path="/mcp")

    # Create MCP app
    mcp_app = mcp_server.http_app(path="/mcp", stateless_http=True)  # type: ignore[attr-defined]

    # Mount everything in a Starlette app with well-known routes at root
    app = Starlette(
        routes=[
            *well_known_routes,
            Mount("/", app=mcp_app),
        ],
        lifespan=mcp_app.lifespan,
    )

    # Only add CORS middleware at the Starlette level
    # Auth middleware is added directly to the MCP server
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
