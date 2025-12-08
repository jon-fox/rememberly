# HTTP API Gateway for MCP server with Supabase JWT authentication

# HTTP API
resource "aws_apigatewayv2_api" "mcp" {
  name          = "rememberly-mcp-api"
  protocol_type = "HTTP"
  description   = "MCP HTTP API with Supabase JWT authentication"

  cors_configuration {
    allow_origins = ["https://${local.domain_name}", "http://localhost:3000"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 300
  }

  tags = {
    Name        = "rememberly-mcp-api"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# JWT authorizer for Supabase
resource "aws_apigatewayv2_authorizer" "jwt" {
  api_id           = aws_apigatewayv2_api.mcp.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "supabase-jwt-authorizer"

  jwt_configuration {
    audience = ["authenticated"]
    issuer   = "${local.supabase_url}/auth/v1"
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.mcp.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.mcp_server.invoke_arn
  payload_format_version = "2.0"
}

# Route with JWT authorization
resource "aws_apigatewayv2_route" "mcp" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "ANY /mcp/{proxy+}"
  
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.mcp.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      errorMessage   = "$context.error.message"
      authorizerError = "$context.authorizer.error"
    })
  }

  tags = {
    Name        = "rememberly-mcp-api-prod"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_server.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.mcp.execution_arn}/*/*"
}

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/rememberly-mcp-api"
  retention_in_days = 7

  tags = {
    Name        = "rememberly-api-gateway-logs"
    Environment = var.environment
    Project     = "rememberly"
  }
}
