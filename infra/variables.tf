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

variable "authorizer_lambda_image_uri" {
    description = "ECR image URI for the Lambda authorizer function"
    type        = string
    default     = "381492150662.dkr.ecr.us-east-1.amazonaws.com/app-ecr-repo:authorizer-latest"
}