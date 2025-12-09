"""Lambda handler entry point for Rememberly MCP Server."""

from mangum import Mangum
from server import create_http_app

# Create the Lambda handler using Mangum to wrap the FastMCP ASGI app
# lifespan="off" because stateless_http mode doesn't need session manager initialization
app = create_http_app()
handler = Mangum(app, lifespan="off")
