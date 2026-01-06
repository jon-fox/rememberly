# HTTP API Gateway for MCP server

resource "aws_apigatewayv2_api" "mcp" {
  name          = "rememberly-mcp-api"
  protocol_type = "HTTP"
  description   = "MCP HTTP API"

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

# EC2 integration - direct HTTP proxy to EC2 Elastic IP
resource "aws_apigatewayv2_integration" "ec2" {
  api_id           = aws_apigatewayv2_api.mcp.id
  integration_type = "HTTP_PROXY"
  integration_uri  = "http://${aws_eip.mcp.public_ip}:8080"

  integration_method = "ANY"
  connection_type    = "INTERNET"

  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "mcp_post" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /mcp"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "mcp_get" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /mcp"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "mcp_proxy" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "ANY /mcp/{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "well_known" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /.well-known/{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

# OAuth operational endpoints
resource "aws_apigatewayv2_route" "oauth_register" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /register"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "oauth_authorize" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /authorize"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "oauth_token" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /token"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "oauth_callback" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /auth/callback"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "oauth_consent" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "GET /consent"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
}

resource "aws_apigatewayv2_route" "oauth_consent_post" {
  api_id    = aws_apigatewayv2_api.mcp.id
  route_key = "POST /consent"

  target = "integrations/${aws_apigatewayv2_integration.ec2.id}"
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
    })
  }

  tags = {
    Name        = "rememberly-mcp-api-prod"
    Environment = var.environment
    Project     = "rememberly"
  }
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

# Custom domain for mcp.rememberly.xyz
resource "aws_apigatewayv2_domain_name" "mcp" {
  domain_name = local.mcp_domain

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.mcp.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = {
    Name        = local.mcp_domain
    Environment = var.environment
    Project     = "rememberly"
  }
}

# API Gateway mapping for MCP domain
resource "aws_apigatewayv2_api_mapping" "mcp" {
  api_id      = aws_apigatewayv2_api.mcp.id
  domain_name = aws_apigatewayv2_domain_name.mcp.id
  stage       = aws_apigatewayv2_stage.prod.id
}
