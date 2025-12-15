# User Management Lambda - separate from MCP server

# Lambda function for user management using container image
resource "aws_lambda_function" "user_service" {
  function_name = "rememberly-user-service"
  role          = aws_iam_role.user_service.arn
  package_type  = "Image"
  image_uri     = "${replace(var.mcp_lambda_image_uri, ":latest", ":user-service-latest")}"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.metadata.name
    }
  }

  tags = {
    Name        = "rememberly-user-service"
    Environment = var.environment
    Project     = "rememberly"
  }

  # Prevent Terraform from trying to update on every apply
  lifecycle {
    ignore_changes = [image_uri]
  }
}

# IAM role for user service Lambda
resource "aws_iam_role" "user_service" {
  name = "rememberly-user-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "rememberly-user-service-role"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# IAM policy for user service - DynamoDB access
resource "aws_iam_role_policy" "user_service_dynamodb" {
  name = "user-service-dynamodb-access"
  role = aws_iam_role.user_service.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.metadata.arn,
          "${aws_dynamodb_table.metadata.arn}/index/*"
        ]
      }
    ]
  })
}

# CloudWatch Logs policy for user service
resource "aws_iam_role_policy_attachment" "user_service_logs" {
  role       = aws_iam_role.user_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda integration for user service
resource "aws_apigatewayv2_integration" "user_service" {
  api_id           = aws_apigatewayv2_api.mcp.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.user_service.invoke_arn
  payload_format_version = "2.0"
}

# Route for user creation - JWT auth required
resource "aws_apigatewayv2_route" "user_service_post" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /users"
  
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
  target             = "integrations/${aws_apigatewayv2_integration.user_service.id}"
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "user_service_api_gateway" {
  statement_id  = "AllowAPIGatewayInvokeUserService"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_service.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.mcp.execution_arn}/*/*/users"
}

# CloudWatch log group for user service
resource "aws_cloudwatch_log_group" "user_service" {
  name              = "/aws/lambda/rememberly-user-service"
  retention_in_days = 7

  tags = {
    Name        = "rememberly-user-service-logs"
    Environment = var.environment
    Project     = "rememberly"
  }
}
