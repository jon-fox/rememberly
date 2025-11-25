"""Rememberly MCP Server - Context and Chat History Management."""

from fastmcp import FastMCP

from mcp_server.services.tool_service import ToolService
from mcp_server.tools.example_memory import ExampleMemoryTool

mcp = FastMCP(
    "Rememberly",
    dependencies=["fastmcp", "pydantic"],
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

# Initialize tool service and register tools
tool_service = ToolService()
tool_service.register_tools(
    [
        ExampleMemoryTool(),
        # Add more tools here as they are implemented
    ]
)

# Register tools with MCP
tool_service.register_mcp_handlers(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
