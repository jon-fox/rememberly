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

variable "google_client_id" {
    description = "Google OAuth Client ID for MCP server authentication"
    type        = string
    sensitive   = false
}

variable "google_client_secret" {
    description = "Google OAuth Client Secret for MCP server authentication"
    type        = string
    sensitive   = true
}

variable "mcp_base_url" {
    description = "Base URL for MCP server OAuth callbacks"
    type        = string
    default     = "https://mcp.rememberly.xyz"
}