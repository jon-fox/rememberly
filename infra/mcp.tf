# MCP Server Infrastructure using AWS Bedrock AgentCore Gateway

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# IAM role for the AgentCore Gateway
resource "aws_iam_role" "mcp_gateway" {
  name = "rememberly-mcp-gateway-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "rememberly-mcp-gateway-role"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# IAM policy for gateway to invoke Lambda targets
resource "aws_iam_role_policy" "mcp_gateway_lambda" {
  name = "mcp-gateway-lambda-invoke"
  role = aws_iam_role.mcp_gateway.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "${aws_lambda_function.mcp_server.arn}*"
      }
    ]
  })
}

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

# Lambda policy for S3 access to storage bucket
resource "aws_iam_role_policy" "mcp_lambda_s3" {
  name = "mcp-lambda-s3-access"
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
      STORAGE_BUCKET = aws_s3_bucket.storage.id
      ENVIRONMENT    = var.environment
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

# Bedrock AgentCore Gateway
resource "aws_bedrockagentcore_gateway" "mcp" {
  name            = "rememberly-mcp-gateway"
  role_arn        = aws_iam_role.mcp_gateway.arn
  authorizer_type = "AWS_IAM"
  protocol_type   = "MCP"

  tags = {
    Name        = "rememberly-mcp-gateway"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Gateway target pointing to Lambda with API key authentication
resource "aws_bedrockagentcore_gateway_target" "mcp_lambda" {
  name               = "mcp-lambda-target"
  gateway_identifier = aws_bedrockagentcore_gateway.mcp.gateway_id
  description        = "MCP server target with API key authentication"

  credential_provider_configuration {
    api_key {
      provider_arn              = aws_lambda_function.mcp_authorizer.arn
      credential_location       = "HEADER"
      credential_parameter_name = "X-API-Key"
    }
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.mcp_server.arn

        tool_schema {
          inline_payload {
            name        = "rememberly_memory"
            description = "Store and retrieve context memory for users"

            input_schema {
              type = "object"

              property {
                name        = "action"
                type        = "string"
                description = "Action to perform: store, retrieve, list, or delete"
                required    = true
              }

              property {
                name        = "user_id"
                type        = "string"
                description = "User identifier"
                required    = true
              }

              property {
                name        = "content"
                type        = "string"
                description = "Memory content to store"
              }

              property {
                name        = "memory_id"
                type        = "string"
                description = "Memory identifier for retrieval or deletion"
              }
            }
          }
        }
      }
    }
  }
}

# Lambda permission for Bedrock to invoke
resource "aws_lambda_permission" "bedrock_invoke" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_server.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:gateway/${aws_bedrockagentcore_gateway.mcp.gateway_id}"
}
