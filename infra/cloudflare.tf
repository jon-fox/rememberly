# Cloudflare DNS and Worker Configuration
# Replaces Route53 for DNS management

# Data source to get zone ID (after zone is added to Cloudflare)
data "cloudflare_zone" "main" {
  name = local.domain_name
}

# CloudFront DNS records
# Using CNAME flattening - Cloudflare will resolve to IPs automatically
resource "cloudflare_record" "apex" {
  zone_id = data.cloudflare_zone.main.id
  name    = "@"
  content = aws_cloudfront_distribution.main.domain_name
  type    = "CNAME"
  proxied = true
  comment = "Root domain to CloudFront"
}

resource "cloudflare_record" "www" {
  zone_id = data.cloudflare_zone.main.id
  name    = "www"
  content = aws_cloudfront_distribution.main.domain_name
  type    = "CNAME"
  proxied = true
  comment = "WWW subdomain to CloudFront"
}

# API Gateway DNS record
resource "cloudflare_record" "api" {
  zone_id = data.cloudflare_zone.main.id
  name    = "api"
  content = aws_apigatewayv2_domain_name.api_internal.domain_name_configuration[0].target_domain_name
  type    = "CNAME"
  proxied = true
  comment = "API Gateway endpoint"
}

# MCP subdomain - managed by Worker custom domain
# The Worker route in wrangler.jsonc will handle mcp.rememberly.xyz
# Cloudflare automatically creates DNS record when custom_domain is deployed

# ACM Certificate validation records (for api.rememberly.xyz)
# Create TXT records in Cloudflare for ACM validation
resource "cloudflare_record" "api_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.mcp.domain_validation_options : dvo.domain_name => {
      name   = trimsuffix(dvo.resource_record_name, ".${local.domain_name}.")
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = data.cloudflare_zone.main.id
  name    = each.value.name
  content = each.value.record
  type    = each.value.type
  ttl     = 60
  comment = "ACM validation for API Gateway"
}

# ACM Certificate validation records (for CloudFront main cert)
resource "cloudflare_record" "main_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = trimsuffix(dvo.resource_record_name, ".${local.domain_name}.")
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = data.cloudflare_zone.main.id
  name    = each.value.name
  content = each.value.record
  type    = each.value.type
  ttl     = 60
  comment = "ACM validation for CloudFront"
}

# Wait for certificate validations
resource "aws_acm_certificate_validation" "main" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in cloudflare_record.main_cert_validation : "${record.name}.${local.domain_name}"]
}

resource "aws_acm_certificate_validation" "mcp" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.mcp.arn
  validation_record_fqdns = [for record in cloudflare_record.api_cert_validation : "${record.name}.${local.domain_name}"]
}
