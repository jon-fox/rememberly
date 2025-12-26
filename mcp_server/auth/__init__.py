"""Authentication module for Rememberly MCP Server."""

from .supabase_auth import get_supabase_auth

__all__ = ["get_supabase_auth"]
