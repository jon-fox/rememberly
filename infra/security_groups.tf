# Security Groups for MCP Infrastructure

# EC2 Security Group
resource "aws_security_group" "ec2" {
  name        = "rememberly-ec2-sg"
  description = "Security group for MCP EC2 instances"
  vpc_id      = data.aws_vpc.default.id

  # Allow traffic from anywhere on port 8080 (API Gateway has no fixed IPs)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic on port 8080"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "rememberly-ec2-sg"
    Environment = var.environment
    Project     = "rememberly"
  }
}
