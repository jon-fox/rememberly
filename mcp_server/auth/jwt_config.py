"""OAuth 2.1 authentication configuration for Supabase Platform."""

from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl


def get_oauth_config() -> RemoteAuthProvider:
    """Create and configure OAuth authentication for Supabase Platform.
    
    Uses RemoteAuthProvider to integrate with Supabase Platform OAuth.
    Validates JWT tokens issued by Supabase and manages OAuth authorization flow.
    Supports PKCE for public clients (desktop apps, web apps).
    
    Returns:
        RemoteAuthProvider: Configured OAuth provider with JWT validation
    """
    # Configure JWT token verification for Supabase Platform tokens
    token_verifier = JWTVerifier(
        jwks_uri="https://api.supabase.com/.well-known/jwks.json",
        issuer="https://api.supabase.com",
        # Supabase OAuth tokens use the client_id as audience
        audience="060c7631-e70d-4b24-afed-145c72e7da21",
        algorithm="RS256"
    )
    
    # Create remote auth provider for Supabase Platform OAuth
    return RemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_servers=[AnyHttpUrl("https://api.supabase.com")],
        base_url="https://mcp.rememberly.xyz",
    )
