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

resource "aws_ssm_parameter" "mcp_endpoint" {
  name        = "/application/mcp_api/endpoint"
  description = "MCP API endpoint URL"
  type        = "String"
  value       = "https://${local.mcp_domain}"

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

resource "aws_ssm_parameter" "mcp_asg_name" {
  name        = "/application/mcp_api/asg_name"
  description = "Name of the MCP Auto Scaling Group"
  type        = "String"
  value       = aws_autoscaling_group.mcp.name

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

resource "aws_ssm_parameter" "mcp_eip" {
  name        = "/application/mcp_api/elastic_ip"
  description = "Elastic IP for MCP EC2 instance"
  type        = "String"
  value       = aws_eip.mcp.public_ip

  tags = {
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "mcp-api"
  }
}

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
