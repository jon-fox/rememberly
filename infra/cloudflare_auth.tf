# Cloudflare Worker for Authentication and MCP Proxy
# mcp.rememberly.xyz now points to Cloudflare Worker (user-facing)
# api.rememberly.xyz points to AWS API Gateway (internal, called by Cloudflare)

# DNS records are now managed by Cloudflare directly
# Custom domain will be configured via wrangler.jsonc routes

# Custom domain for internal API Gateway
resource "aws_apigatewayv2_domain_name" "api_internal" {
  domain_name = "api.rememberly.xyz"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.mcp.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = {
    Name        = "api.rememberly.xyz"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# API Gateway mapping for internal API
resource "aws_apigatewayv2_api_mapping" "api_internal" {
  api_id      = aws_apigatewayv2_api.mcp.id
  domain_name = aws_apigatewayv2_domain_name.api_internal.id
  stage       = aws_apigatewayv2_stage.prod.id
}

# api.rememberly.xyz DNS record now managed in Cloudflare
