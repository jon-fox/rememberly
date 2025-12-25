"""OAuth 2.1 authentication configuration for Supabase Auth."""

import os
from fastmcp.server.auth.providers.supabase import SupabaseProvider


def get_oauth_config() -> SupabaseProvider:
    """Create and configure OAuth authentication for Supabase OAuth Server.

    Uses Supabase as the OAuth 2.1 identity provider.
    Supabase handles user authentication - your existing user base.
    MCP clients authenticate directly with Supabase (no proxy needed).

    Requirements:
    1. Enable "Supabase OAuth Server" in dashboard
    2. Enable "Allow Dynamic OAuth Apps" for MCP client registration
    3. Set Authorization Path to /oauth/consent in Supabase dashboard
    4. Host consent page at https://rememberly.xyz/oauth/consent

    Returns:
        SupabaseProvider: Configured Supabase authentication
    """
    supabase_url = os.getenv("SUPABASE_URL", "https://ijyyifghxitisjbfnoxb.supabase.co")
    base_url = os.getenv("BASE_URL", "https://mcp.rememberly.xyz")
    
    return SupabaseProvider(
        project_url=supabase_url,
        base_url=base_url,
        authorization_path="/oauth/consent",  # Consent page hosted on main website
    )
