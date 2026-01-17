# Security Groups for MCP Infrastructure

# EC2 Security Group
resource "aws_security_group" "ec2" {
  name        = "rememberly-ec2-sg"
  description = "Security group for MCP EC2 instances"
  vpc_id      = data.aws_vpc.default.id

  # Allow HTTPS traffic for Caddy
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS traffic"
  }

  # Allow HTTP traffic for Let's Encrypt validation
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic for SSL certificate validation"
  }

  # Allow traffic on port 8080 for direct access (optional)
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
