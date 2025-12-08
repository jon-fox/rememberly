# Route53 DNS Configuration for rememberly.xyz

# Route53 Hosted Zone
resource "aws_route53_zone" "main" {
  name = local.domain_name

  tags = {
    Name        = local.domain_name
    Environment = var.environment
    Project     = "rememberly"
  }
}

# ACM Certificate for CloudFront (must be in us-east-1)
resource "aws_acm_certificate" "main" {
  provider          = aws.us_east_1
  domain_name       = local.domain_name
  validation_method = "DNS"
  subject_alternative_names = [local.www_domain]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = local.domain_name
    Environment = var.environment
    Project     = "rememberly"
  }
}

# DNS validation records for ACM certificate
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Wait for certificate validation
resource "aws_acm_certificate_validation" "main" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Route53 A record for apex domain
resource "aws_route53_record" "apex" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 A record for www subdomain
resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.www_domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 AAAA record for apex domain (IPv6)
resource "aws_route53_record" "apex_ipv6" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.domain_name
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 AAAA record for www subdomain (IPv6)
resource "aws_route53_record" "www_ipv6" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.www_domain
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# ACM Certificate for MCP API Gateway (must be in us-east-1 for edge-optimized endpoints)
resource "aws_acm_certificate" "mcp" {
  provider          = aws.us_east_1
  domain_name       = local.mcp_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = local.mcp_domain
    Environment = var.environment
    Project     = "rememberly"
  }
}

# DNS validation records for MCP ACM certificate
resource "aws_route53_record" "mcp_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.mcp.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Wait for MCP certificate validation
resource "aws_acm_certificate_validation" "mcp" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.mcp.arn
  validation_record_fqdns = [for record in aws_route53_record.mcp_cert_validation : record.fqdn]
}

# Route53 A record for MCP subdomain
resource "aws_route53_record" "mcp" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.mcp_domain
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 AAAA record for MCP subdomain (IPv6)
resource "aws_route53_record" "mcp_ipv6" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.mcp_domain
  type    = "AAAA"

  alias {
    name                   = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.mcp.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
