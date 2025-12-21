"""OAuth 2.1 authentication configuration for Supabase Auth."""

import os
from pathlib import Path
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from key_value.aio.stores.disk import DiskStore


def get_oauth_config() -> OAuthProxy:
    """Create and configure OAuth authentication for Supabase Auth.

    Uses OAuthProxy to proxy OAuth flow through our server to Supabase Auth.
    Hosts /authorize and /token endpoints that forward to Supabase.
    Validates JWT tokens issued by Supabase Auth.
    Supports PKCE for public clients (desktop apps, web apps).

    Returns:
        OAuthProxy: Configured OAuth proxy with JWT validation
    """
    # Supabase project URL and credentials
    supabase_url = os.getenv("SUPABASE_URL", "https://ijyyifghxitisjbfnoxb.supabase.co")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Configure JWT token verification for Supabase Auth tokens
    token_verifier = JWTVerifier(
        jwks_uri=f"{supabase_url}/auth/v1/.well-known/jwks.json",
        issuer=f"{supabase_url}/auth/v1",
        audience="authenticated",
        algorithm="RS256",
    )

    # Create OAuth proxy that hosts auth endpoints and forwards to Supabase Auth
    return OAuthProxy(
        # Supabase Auth OAuth endpoints
        upstream_authorization_endpoint=f"{supabase_url}/auth/v1/authorize",
        upstream_token_endpoint=f"{supabase_url}/auth/v1/token",
        # Supabase project credentials (anon key acts as client_id for public clients)
        upstream_client_id=supabase_anon_key,
        upstream_client_secret="",  # Public client, no secret needed
        # Token validation
        token_verifier=token_verifier,
        # Your FastMCP server's public URL (includes /mcp mount prefix)
        # OAuth endpoints will be at: /mcp/authorize, /mcp/token, /mcp/oauth/callback
        base_url="https://mcp.rememberly.xyz/mcp",
        # OAuth callback path (default is /auth/callback)
        redirect_path="/oauth/callback",
        # Forward PKCE to upstream (Supabase supports it)
        forward_pkce=True,
        # Allow Claude.ai redirect URIs in addition to localhost
        allowed_client_redirect_uris=[
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://claude.ai/api/mcp/auth_callback",
            "https://claude.com/api/mcp/auth_callback",
        ],
        # Use /tmp for Lambda - only writable directory
        client_storage=DiskStore(directory=Path("/tmp/oauth-proxy")),
    )
