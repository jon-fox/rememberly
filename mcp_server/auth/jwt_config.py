"""JWT authentication configuration for Supabase integration."""

from fastmcp.server.auth.providers.jwt import JWTVerifier


def get_jwt_verifier() -> JWTVerifier:
    """Create and configure JWT verifier for Supabase authentication.
    
    Configures RS256 JWT verification using Supabase's JWKS endpoint.
    This validates token signatures, issuer, and audience claims.
    
    Returns:
        JWTVerifier: Configured JWT verifier for Supabase tokens
    """
    supabase_url = "https://ijyyifghxitisjbfnoxb.supabase.co"
    
    return JWTVerifier(
        jwks_uri=f"{supabase_url}/auth/v1/.well-known/jwks.json",
        issuer=f"{supabase_url}/auth/v1",
        audience="authenticated",
        algorithm="RS256"
    )
