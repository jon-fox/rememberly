variable "environment" {
    description = "The deployment environment (e.g., dev, staging, prod)"
    type        = string
    default     = "prod" 
}

variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "us-east-1"
}

variable "mcp_lambda_image_uri" {
    description = "ECR image URI for the MCP Lambda function"
    type        = string
    default     = "381492150662.dkr.ecr.us-east-1.amazonaws.com/app-ecr-repo:latest"
}

variable "mcp_image_version" {
    description = "Version identifier for MCP image - change this to force Lambda to pull new image"
    type        = string
    default     = "1"
}

variable "supabase_anon_key" {
    description = "Supabase anonymous (public) API key"
    type        = string
    sensitive   = true
}

variable "supabase_service_role_key" {
    description = "Supabase service role (admin) API key"
    type        = string
    sensitive   = true
}