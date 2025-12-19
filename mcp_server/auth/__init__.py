"""Authentication configuration for the MCP server."""

from .jwt_config import get_oauth_config

__all__ = ["get_oauth_config"]
