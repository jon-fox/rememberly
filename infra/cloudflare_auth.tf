# Cloudflare Worker for Authentication and MCP Proxy
# mcp.rememberly.xyz now points to Cloudflare Worker (user-facing)
# api.rememberly.xyz points to AWS API Gateway (internal, called by Cloudflare)

# User-facing endpoint: mcp.rememberly.xyz → Cloudflare Worker
resource "aws_route53_record" "mcp_cloudflare" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "mcp.rememberly.xyz"
  type    = "CNAME"
  ttl     = 300
  records = ["rememberly-auth.rememberlymcp.workers.dev"]
}

# Internal API endpoint: api.rememberly.xyz → AWS API Gateway
resource "aws_route53_record" "api_internal" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.rememberly.xyz"
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
