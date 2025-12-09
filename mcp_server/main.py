"""Lambda handler entry point for Rememberly MCP Server."""

from mangum import Mangum
from server import mcp

# Create the Lambda handler using Mangum to wrap the FastMCP ASGI app
handler = Mangum(mcp._app, lifespan="off")
