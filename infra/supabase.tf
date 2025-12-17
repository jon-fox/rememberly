# Supabase Authentication Integration
# Using existing Supabase instance at: https://ijyyifghxitisjbfnoxb.supabase.co
#
# JWT validation is performed by FastMCP's JWTVerifier in the Lambda function.
# FastMCP uses RS256 signature verification with Supabase's JWKS endpoint:
# https://ijyyifghxitisjbfnoxb.supabase.co/auth/v1/.well-known/jwks.json

locals {
  supabase_url     = "https://ijyyifghxitisjbfnoxb.supabase.co"
  supabase_project_id = "ijyyifghxitisjbfnoxb"
  supabase_jwks_url = "${local.supabase_url}/auth/v1/.well-known/jwks.json"
}
