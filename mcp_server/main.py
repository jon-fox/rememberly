"""App export for AWS Lambda Web Adapter.

With Lambda Web Adapter, we don't need Mangum. The adapter runs as a Lambda Extension
and forwards requests to our ASGI app running on uvicorn.
"""

# This file is no longer needed with Lambda Web Adapter
# The app is exported directly from server.py
from server import app

__all__ = ["app"]
