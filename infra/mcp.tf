# MCP Server Infrastructure

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Lambda execution role for MCP server
resource "aws_iam_role" "mcp_lambda" {
  name = "rememberly-mcp-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "rememberly-mcp-lambda-role"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Lambda policy for S3 and DynamoDB access
resource "aws_iam_role_policy" "mcp_lambda_storage" {
  name = "mcp-lambda-storage-access"
  role = aws_iam_role.mcp_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.storage.arn,
          "${aws_s3_bucket.storage.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.metadata.arn,
          "${aws_dynamodb_table.metadata.arn}/index/*"
        ]
      }
    ]
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "mcp_lambda_basic" {
  role       = aws_iam_role.mcp_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function for MCP server
resource "aws_lambda_function" "mcp_server" {
  function_name = "rememberly-mcp-server"
  role          = aws_iam_role.mcp_lambda.arn
  timeout       = 30
  memory_size   = 512
  package_type  = "Image"

  image_uri = var.mcp_lambda_image_uri

  environment {
    variables = {
      STORAGE_BUCKET      = aws_s3_bucket.storage.id
      DYNAMODB_TABLE      = aws_dynamodb_table.metadata.name
      ENVIRONMENT         = var.environment
      IMAGE_VERSION       = var.mcp_image_version
      GOOGLE_CLIENT_ID    = var.google_client_id
      GOOGLE_CLIENT_SECRET = var.google_client_secret
      MCP_BASE_URL        = var.mcp_base_url
    }
  }

  tags = {
    Name        = "rememberly-mcp-server"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "mcp_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.mcp_server.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "rememberly-mcp-lambda-logs"
    Environment = var.environment
    Project     = "rememberly"
  }
}
