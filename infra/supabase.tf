# Supabase Authentication Integration
# Using existing Supabase instance at: https://ijyyifghxitisjbfnoxb.supabase.co

locals {
  supabase_url     = "https://ijyyifghxitisjbfnoxb.supabase.co"
  supabase_project_id = "ijyyifghxitisjbfnoxb"
  supabase_jwks_url = "${local.supabase_url}/auth/v1/.well-known/jwks.json"
}

# Store Supabase credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "supabase_anon_key" {
  name        = "rememberly-supabase-anon-key-${var.environment}"
  description = "Supabase anonymous (public) API key"

  tags = {
    Name        = "rememberly-supabase-anon-key"
    Environment = var.environment
    Project     = "rememberly"
  }
}

resource "aws_secretsmanager_secret_version" "supabase_anon_key" {
  secret_id     = aws_secretsmanager_secret.supabase_anon_key.id
  secret_string = var.supabase_anon_key
}

resource "aws_secretsmanager_secret" "supabase_service_role_key" {
  name        = "rememberly-supabase-service-role-key-${var.environment}"
  description = "Supabase service role (admin) API key"

  tags = {
    Name        = "rememberly-supabase-service-role-key"
    Environment = var.environment
    Project     = "rememberly"
  }
}

resource "aws_secretsmanager_secret_version" "supabase_service_role_key" {
  secret_id     = aws_secretsmanager_secret.supabase_service_role_key.id
  secret_string = var.supabase_service_role_key
}

# IAM policy for Lambda to access Supabase secrets
resource "aws_iam_policy" "lambda_supabase_secrets" {
  name        = "rememberly-lambda-supabase-secrets-${var.environment}"
  description = "Allow Lambda to read Supabase credentials from Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.supabase_anon_key.arn,
          aws_secretsmanager_secret.supabase_service_role_key.arn
        ]
      }
    ]
  })
}

# Attach the policy to the Lambda execution role (defined in mcp.tf)
resource "aws_iam_role_policy_attachment" "lambda_supabase_secrets" {
  role       = aws_iam_role.mcp_lambda.name
  policy_arn = aws_iam_policy.lambda_supabase_secrets.arn
}
