# AWS Systems Manager Parameter Store for application configuration
# Stores outputs in a structured hierarchy: /application/<bucket_and_use_case>

# S3 Website Bucket Parameters
resource "aws_ssm_parameter" "website_bucket_name" {
  name        = "/application/s3_website/bucket_name"
  description = "Name of the S3 bucket hosting the website"
  type        = "String"
  value       = aws_s3_bucket.website.id

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "website-hosting"
  }
}

resource "aws_ssm_parameter" "website_bucket_regional_domain" {
  name        = "/application/s3_website/regional_domain_name"
  description = "Regional domain name of the website S3 bucket"
  type        = "String"
  value       = aws_s3_bucket.website.bucket_regional_domain_name

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "website-hosting"
  }
}

# S3 Storage Bucket Parameters
resource "aws_ssm_parameter" "storage_bucket_name" {
  name        = "/application/s3_storage/bucket_name"
  description = "Name of the S3 bucket for user data storage"
  type        = "String"
  value       = aws_s3_bucket.storage.id

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "user-data-storage"
  }
}

# CloudFront Parameters
resource "aws_ssm_parameter" "cloudfront_distribution_id" {
  name        = "/application/cloudfront/distribution_id"
  description = "ID of the CloudFront distribution"
  type        = "String"
  value       = aws_cloudfront_distribution.main.id

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "cdn"
  }
}

resource "aws_ssm_parameter" "cloudfront_distribution_arn" {
  name        = "/application/cloudfront/distribution_arn"
  description = "ARN of the CloudFront distribution"
  type        = "String"
  value       = aws_cloudfront_distribution.main.arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "cdn"
  }
}

resource "aws_ssm_parameter" "cloudfront_domain_name" {
  name        = "/application/cloudfront/domain_name"
  description = "Domain name of the CloudFront distribution"
  type        = "String"
  value       = aws_cloudfront_distribution.main.domain_name

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "cdn"
  }
}

# Route53 Parameters
resource "aws_ssm_parameter" "route53_zone_id" {
  name        = "/application/route53/zone_id"
  description = "ID of the Route53 hosted zone"
  type        = "String"
  value       = aws_route53_zone.main.zone_id

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "dns"
  }
}

resource "aws_ssm_parameter" "route53_name_servers" {
  name        = "/application/route53/name_servers"
  description = "Name servers for the Route53 hosted zone (JSON array)"
  type        = "String"
  value       = jsonencode(aws_route53_zone.main.name_servers)

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "dns"
  }
}

# MCP API Parameters
resource "aws_ssm_parameter" "mcp_endpoint" {
  name        = "/application/mcp_api/endpoint"
  description = "MCP API endpoint URL"
  type        = "String"
  value       = "https://${local.mcp_domain}/mcp"

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

resource "aws_ssm_parameter" "mcp_lambda_function_name" {
  name        = "/application/mcp_api/lambda_function_name"
  description = "Name of the MCP Lambda function"
  type        = "String"
  value       = aws_lambda_function.mcp_server.function_name

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

resource "aws_ssm_parameter" "mcp_lambda_function_arn" {
  name        = "/application/mcp_api/lambda_function_arn"
  description = "ARN of the MCP Lambda function"
  type        = "String"
  value       = aws_lambda_function.mcp_server.arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

# ACM Certificate Parameters
resource "aws_ssm_parameter" "cloudfront_certificate_arn" {
  name        = "/application/acm_certificate/cloudfront_arn"
  description = "ARN of the ACM certificate for CloudFront"
  type        = "String"
  value       = aws_acm_certificate.main.arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "ssl-certificate"
  }
}

resource "aws_ssm_parameter" "mcp_certificate_arn" {
  name        = "/application/acm_certificate/mcp_arn"
  description = "ARN of the ACM certificate for MCP API Gateway"
  type        = "String"
  value       = aws_acm_certificate.mcp.arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "ssl-certificate"
  }
}

# Website URL Parameters
resource "aws_ssm_parameter" "website_url" {
  name        = "/application/website/primary_url"
  description = "Primary website URL"
  type        = "String"
  value       = "https://${local.domain_name}"

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "website-url"
  }
}

resource "aws_ssm_parameter" "www_website_url" {
  name        = "/application/website/www_url"
  description = "WWW website URL"
  type        = "String"
  value       = "https://${local.www_domain}"

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "website-url"
  }
}

# DynamoDB Parameters
resource "aws_ssm_parameter" "dynamodb_metadata_table" {
  name        = "/application/dynamodb_metadata/table_name"
  description = "Name of the DynamoDB metadata table"
  type        = "String"
  value       = aws_dynamodb_table.metadata.name

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "metadata-storage"
  }
}

resource "aws_ssm_parameter" "dynamodb_metadata_table_arn" {
  name        = "/application/dynamodb_metadata/table_arn"
  description = "ARN of the DynamoDB metadata table"
  type        = "String"
  value       = aws_dynamodb_table.metadata.arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "metadata-storage"
  }
}

# API Gateway Parameters
resource "aws_ssm_parameter" "api_gateway_id" {
  name        = "/application/api_gateway/api_id"
  description = "ID of the API Gateway HTTP API"
  type        = "String"
  value       = aws_apigatewayv2_api.mcp.id

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "api-gateway"
  }
}

resource "aws_ssm_parameter" "api_gateway_execution_arn" {
  name        = "/application/api_gateway/execution_arn"
  description = "Execution ARN of the API Gateway"
  type        = "String"
  value       = aws_apigatewayv2_api.mcp.execution_arn

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "api-gateway"
  }
}
