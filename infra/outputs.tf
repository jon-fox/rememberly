# S3 Bucket outputs
output "s3_website_bucket_name" {
  description = "Name of the S3 bucket hosting the website"
  value       = aws_s3_bucket.website.id
}

output "s3_website_bucket_arn" {
  description = "ARN of the website S3 bucket"
  value       = aws_s3_bucket.website.arn
}

output "s3_website_bucket_regional_domain_name" {
  description = "Regional domain name of the website S3 bucket"
  value       = aws_s3_bucket.website.bucket_regional_domain_name
}

output "s3_storage_bucket_name" {
  description = "Name of the S3 bucket for user data storage"
  value       = aws_s3_bucket.storage.id
}

output "s3_storage_bucket_arn" {
  description = "ARN of the storage S3 bucket"
  value       = aws_s3_bucket.storage.arn
}

# CloudFront outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.domain_name
}

# Route53 outputs
output "route53_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = aws_route53_zone.main.zone_id
}

output "route53_name_servers" {
  description = "Name servers for the Route53 hosted zone"
  value       = aws_route53_zone.main.name_servers
}

# ACM Certificate outputs
output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.main.arn
}

output "acm_certificate_status" {
  description = "Status of the ACM certificate"
  value       = aws_acm_certificate.main.status
}

# Website URLs
output "website_url" {
  description = "Primary website URL"
  value       = "https://${local.domain_name}"
}

output "www_website_url" {
  description = "WWW website URL"
  value       = "https://${local.www_domain}"
}

# Deployment information
output "cloudfront_invalidation_command" {
  description = "AWS CLI command to invalidate CloudFront cache"
  value       = "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.main.id} --paths '/*'"
}

output "s3_sync_command" {
  description = "AWS CLI command to sync files to S3"
  value       = "aws s3 sync ./dist s3://${aws_s3_bucket.website.id} --delete"
}
