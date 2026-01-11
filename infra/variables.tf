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

variable "mcp_ec2_image_uri" {
  description = "ECR image URI for the MCP EC2 containers"
  type        = string
  default     = "381492150662.dkr.ecr.us-east-1.amazonaws.com/app-ecr-repo:latest"
}

variable "mcp_instance_type" {
  description = "EC2 instance type for MCP server"
  type        = string
  default     = "t3.nano"
}

variable "mcp_image_version" {
  description = "Version identifier for MCP image - change this to force EC2 to pull new image"
  type        = string
  default     = "1"
}

variable "mcp_asg_min_size" {
  description = "Minimum number of instances in MCP Auto Scaling Group"
  type        = number
  default     = 0
}

variable "mcp_asg_max_size" {
  description = "Maximum number of instances in MCP Auto Scaling Group"
  type        = number
  default     = 1
}

variable "mcp_asg_desired_capacity" {
  description = "Desired number of instances in MCP Auto Scaling Group"
  type        = number
  default     = 0
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