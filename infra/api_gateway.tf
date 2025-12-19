# HTTP API Gateway for MCP server
# OAuth 2.1 authentication is handled by FastMCP in the Lambda function

# HTTP API
resource "aws_apigatewayv2_api" "mcp" {
  name          = "rememberly-mcp-api"
  protocol_type = "HTTP"
  description   = "MCP HTTP API - OAuth 2.1 authorization handled by FastMCP in Lambda"

  cors_configuration {
    allow_origins     = ["https://${local.domain_name}", "https://${local.www_domain}", "http://localhost:3000"]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers     = ["content-type", "authorization", "x-requested-with"]
    expose_headers    = ["content-type", "x-amz-request-id"]
    allow_credentials = false
    max_age           = 300
  }

  tags = {
    Name        = "rememberly-mcp-api"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.mcp.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.mcp_server.invoke_arn
  payload_format_version = "2.0"
}

# Route for MCP endpoint - handles JSON-RPC requests
# MCP clients POST JSON-RPC messages to /mcp with method field specifying the tool/resource/prompt
# Authentication is handled by FastMCP OAuth in Lambda
resource "aws_apigatewayv2_route" "mcp_post" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /mcp"
  
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route for SSE stream - allows MCP clients to receive server-initiated messages
# Optional GET endpoint for Server-Sent Events if needed
# Authentication is handled by FastMCP OAuth in Lambda
resource "aws_apigatewayv2_route" "mcp_get" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /mcp"
  
  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# OAuth and MCP routes handled by FastMCP in Lambda
# With base_url=https://mcp.rememberly.xyz and path="/mcp":
# - OAuth endpoints at root: /authorize, /token, /oauth/callback, /.well-known/oauth-authorization-server
# - MCP operational endpoint: /mcp (for JSON-RPC messages)
# Lambda Web Adapter routes all requests to the FastMCP app which handles routing internally

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

# Custom domain for MCP API Gateway
resource "aws_apigatewayv2_domain_name" "mcp" {
  domain_name = local.mcp_domain

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.mcp.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.mcp]

  tags = {
    Name        = local.mcp_domain
    Environment = var.environment
    Project     = "rememberly"
  }
}

# API Gateway mapping to custom domain
resource "aws_apigatewayv2_api_mapping" "mcp" {
  api_id      = aws_apigatewayv2_api.mcp.id
  domain_name = aws_apigatewayv2_domain_name.mcp.id
  stage       = aws_apigatewayv2_stage.prod.id
}
