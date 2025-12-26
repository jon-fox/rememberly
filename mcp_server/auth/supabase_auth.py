"""Supabase authentication configuration for FastMCP."""

import os
from fastmcp.server.auth.providers.supabase import SupabaseProvider


def get_supabase_auth() -> SupabaseProvider:
    """
    Configure and return Supabase authentication provider.
    
    Required environment variables:
        SUPABASE_PROJECT_URL: Your Supabase project URL (e.g., https://xxx.supabase.co)
        MCP_BASE_URL: Your MCP server's public URL (e.g., https://rememberly.xyz)
    
    Returns:
        SupabaseProvider configured for OAuth authentication
    """
    project_url = os.getenv(
        "SUPABASE_PROJECT_URL",
        "https://ijyyifghxitisjbfnoxb.supabase.co"
    )
    base_url = os.getenv(
        "MCP_BASE_URL",
        "https://rememberly.xyz"
    )
    
    return SupabaseProvider(
        project_url=project_url,
        base_url=base_url,
    )
