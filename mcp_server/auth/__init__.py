"""Authentication configuration for the MCP server."""

from .jwt_config import get_jwt_verifier

__all__ = ["get_jwt_verifier"]
