# Lambda Authorizer for MCP Gateway

# IAM role for the authorizer Lambda
resource "aws_iam_role" "mcp_authorizer" {
  name = "rememberly-mcp-authorizer-role"

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
    Name        = "rememberly-mcp-authorizer-role"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Attach basic Lambda execution policy for logging
resource "aws_iam_role_policy_attachment" "mcp_authorizer_basic" {
  role       = aws_iam_role.mcp_authorizer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM policy for authorizer to access Secrets Manager (for API keys)
resource "aws_iam_role_policy" "mcp_authorizer_secrets" {
  name = "mcp-authorizer-secrets-access"
  role = aws_iam_role.mcp_authorizer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.mcp_api_keys.arn
      }
    ]
  })
}

# Secrets Manager secret for storing API keys
resource "aws_secretsmanager_secret" "mcp_api_keys" {
  name        = "rememberly-mcp-api-keys"
  description = "API keys for MCP gateway authentication"

  tags = {
    Name        = "rememberly-mcp-api-keys"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Initial secret version with placeholder
resource "aws_secretsmanager_secret_version" "mcp_api_keys" {
  secret_id = aws_secretsmanager_secret.mcp_api_keys.id
  secret_string = jsonencode({
    api_keys = {
      "example-key-id" = "example-api-key-value"
    }
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Lambda function for authorization
resource "aws_lambda_function" "mcp_authorizer" {
  function_name = "rememberly-mcp-authorizer"
  role          = aws_iam_role.mcp_authorizer.arn
  timeout       = 10
  memory_size   = 256
  package_type  = "Image"

  image_uri = var.authorizer_lambda_image_uri

  environment {
    variables = {
      SECRET_NAME = aws_secretsmanager_secret.mcp_api_keys.name
    }
  }

  tags = {
    Name        = "rememberly-mcp-authorizer"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Remove the archive_file data source as we're using Docker images now

# CloudWatch log group for authorizer Lambda
resource "aws_cloudwatch_log_group" "mcp_authorizer" {
  name              = "/aws/lambda/${aws_lambda_function.mcp_authorizer.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "rememberly-mcp-authorizer-logs"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Lambda permission for Bedrock to invoke authorizer
resource "aws_lambda_permission" "bedrock_invoke_authorizer" {
  statement_id  = "AllowBedrockInvokeAuthorizer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_authorizer.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:gateway/${aws_bedrockagentcore_gateway.mcp.gateway_id}"
}
