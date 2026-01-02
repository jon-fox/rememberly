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

# Custom domain for internal API Gateway
resource "aws_apigatewayv2_domain_name" "api_internal" {
  domain_name = "api.rememberly.xyz"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.mcp.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.mcp]

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

# Internal API endpoint: api.rememberly.xyz → AWS API Gateway
resource "aws_route53_record" "api_internal" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.rememberly.xyz"
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.api_internal.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api_internal.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
