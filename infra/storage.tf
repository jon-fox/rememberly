# Storage infrastructure for Rememberly

# S3 bucket for user data storage
resource "aws_s3_bucket" "storage" {
  bucket = local.storage_bucket_name

  tags = {
    Name        = local.storage_bucket_name
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "user-data-storage"
  }
}

# S3 bucket ownership controls for storage
resource "aws_s3_bucket_ownership_controls" "storage" {
  bucket = aws_s3_bucket.storage.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# Block public access to storage bucket
resource "aws_s3_bucket_public_access_block" "storage" {
  bucket = aws_s3_bucket.storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Storage bucket versioning
resource "aws_s3_bucket_versioning" "storage" {
  bucket = aws_s3_bucket.storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Storage bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "storage" {
  bucket = aws_s3_bucket.storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Storage bucket lifecycle policy
resource "aws_s3_bucket_lifecycle_configuration" "storage" {
  bucket = aws_s3_bucket.storage.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 120
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 240
      storage_class = "GLACIER_IR"
    }
  }

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# DynamoDB table for metadata storage
resource "aws_dynamodb_table" "metadata" {
  name           = "rememberly-metadata-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  attribute {
    name = "gsi1pk"
    type = "S"
  }

  attribute {
    name = "gsi1sk"
    type = "S"
  }

  # GSI for user-based queries
  global_secondary_index {
    name            = "GSI1"
    hash_key        = "gsi1pk"
    range_key       = "gsi1sk"
    projection_type = "ALL"
  }

  # TTL for auto-expiring sessions
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery for production
  point_in_time_recovery {
    enabled = var.environment == "prod" ? true : false
  }

  tags = {
    Name        = "rememberly-metadata"
    Environment = var.environment
    Project     = "rememberly"
    Purpose     = "metadata-storage"
  }
}

# DynamoDB table policy for encryption at rest
# Note: DynamoDB encryption at rest is enabled by default in AWS

