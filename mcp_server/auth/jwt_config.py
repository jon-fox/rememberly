"""OAuth 2.1 authentication configuration for Supabase Platform."""

import os
from pathlib import Path
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from key_value.aio.stores.disk import DiskStore


def get_oauth_config() -> OAuthProxy:
    """Create and configure OAuth authentication for Supabase Platform.

    Uses OAuthProxy to proxy OAuth flow through our server to Supabase Platform.
    Hosts /authorize and /token endpoints that forward to Supabase.
    Validates JWT tokens issued by Supabase.
    Supports PKCE for public clients (desktop apps, web apps).

    Returns:
        OAuthProxy: Configured OAuth proxy with JWT validation
    """
    # Get Supabase OAuth client credentials from environment
    client_id = os.getenv("SUPABASE_CLIENT_ID", "060c7631-e70d-4b24-afed-145c72e7da21")
    client_secret = os.getenv(
        "SUPABASE_CLIENT_SECRET", ""
    )  # Public client, may be empty

    # Configure JWT token verification for Supabase Platform tokens
    token_verifier = JWTVerifier(
        jwks_uri="https://api.supabase.com/.well-known/jwks.json",
        issuer="https://api.supabase.com",
        audience=client_id,
        algorithm="RS256",
    )

    # Create OAuth proxy that hosts auth endpoints and forwards to Supabase
    return OAuthProxy(
        # Supabase Platform OAuth endpoints
        upstream_authorization_endpoint="https://api.supabase.com/v1/oauth/authorize",
        upstream_token_endpoint="https://api.supabase.com/v1/oauth/token",
        # Your Supabase OAuth client credentials
        upstream_client_id=client_id,
        upstream_client_secret=client_secret,
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
