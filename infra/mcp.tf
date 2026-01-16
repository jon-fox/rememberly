# MCP Server Infrastructure

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Get latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM role for MCP EC2 instances
resource "aws_iam_role" "mcp_ec2" {
  name = "rememberly-mcp-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "rememberly-mcp-ec2-role"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# IAM policy for S3 and DynamoDB access
resource "aws_iam_role_policy" "mcp_ec2_storage" {
  name = "mcp-ec2-storage-access"
  role = aws_iam_role.mcp_ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.storage.arn,
          "${aws_s3_bucket.storage.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.metadata.arn,
          "${aws_dynamodb_table.metadata.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach SSM policy for EC2 management (connect via Session Manager)
resource "aws_iam_role_policy_attachment" "mcp_ec2_ssm" {
  role       = aws_iam_role.mcp_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "mcp_ec2" {
  name = "rememberly-mcp-ec2-profile"
  role = aws_iam_role.mcp_ec2.name

  tags = {
    Name        = "rememberly-mcp-ec2-profile"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Elastic IP for EC2 instance
resource "aws_eip" "mcp" {
  domain = "vpc"

  tags = {
    Name        = "rememberly-mcp-eip"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# User data script for EC2 instances
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e
    
    # Ensure SSM agent is running (pre-installed on Amazon Linux 2023)
    systemctl enable --now amazon-ssm-agent
    
    # Install Docker
    yum update -y
    yum install -y docker
    systemctl enable --now docker
    
    # Pull and run container
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
    docker pull ${var.mcp_ec2_image_uri}
    docker run -d --name rememberly-mcp --restart unless-stopped -p 8080:8080 \
      -e STORAGE_BUCKET=${aws_s3_bucket.storage.id} \
      -e DYNAMODB_TABLE=${aws_dynamodb_table.metadata.name} \
      -e ENVIRONMENT=${var.environment} \
      -e GOOGLE_CLIENT_ID=${var.google_client_id} \
      -e GOOGLE_CLIENT_SECRET=${var.google_client_secret} \
      -e MCP_BASE_URL=${var.mcp_base_url} \
      ${var.mcp_ec2_image_uri}
    EOF
}

# Launch Template for MCP EC2 instances
resource "aws_launch_template" "mcp" {
  name_prefix   = "rememberly-mcp-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = var.mcp_instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.mcp_ec2.name
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.ec2.id]
  }

  user_data = base64encode(local.user_data)

  monitoring {
    enabled = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "rememberly-mcp-server"
      Environment = var.environment
      Project     = "rememberly"
    }
  }

  tags = {
    Name        = "rememberly-mcp-launch-template"
    Environment = var.environment
    Project     = "rememberly"
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "mcp" {
  name                      = "rememberly-mcp-asg"
  vpc_zone_identifier       = data.aws_subnets.default.ids
  health_check_type         = "EC2"
  health_check_grace_period = 300

  min_size         = var.mcp_asg_min_size
  max_size         = var.mcp_asg_max_size
  desired_capacity = var.mcp_asg_desired_capacity

  launch_template {
    id      = aws_launch_template.mcp.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "rememberly-mcp-asg-instance"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }

  tag {
    key                 = "Project"
    value               = "rememberly"
    propagate_at_launch = true
  }
}

# Attach EIP to instance when it launches (only if ASG has instances)
resource "null_resource" "attach_eip" {
  count = var.mcp_asg_desired_capacity > 0 ? 1 : 0

  triggers = {
    asg_name          = aws_autoscaling_group.mcp.name
    desired_capacity  = var.mcp_asg_desired_capacity
  }

  provisioner "local-exec" {
    command = <<-EOT
      # Wait for instance and attach EIP (timeout after 5 minutes)
      TIMEOUT=300
      ELAPSED=0
      while [ $ELAPSED -lt $TIMEOUT ]; do
        INSTANCE_ID=$(aws autoscaling describe-auto-scaling-groups \
          --auto-scaling-group-names ${aws_autoscaling_group.mcp.name} \
          --region ${var.aws_region} \
          --query 'AutoScalingGroups[0].Instances[?LifecycleState==`InService`].InstanceId | [0]' \
          --output text)
        
        if [ "$INSTANCE_ID" != "None" ] && [ "$INSTANCE_ID" != "" ] && [ "$INSTANCE_ID" != "null" ]; then
          echo "Found instance $INSTANCE_ID, attaching EIP..."
          aws ec2 associate-address \
            --instance-id $INSTANCE_ID \
            --allocation-id ${aws_eip.mcp.id} \
            --region ${var.aws_region} && echo "EIP attached successfully" && break
        fi
        sleep 10
        ELAPSED=$((ELAPSED + 10))
      done
      
      if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "Timeout waiting for instance to be ready"
        exit 1
      fi
    EOT
  }
}

# CloudWatch log group for EC2
resource "aws_cloudwatch_log_group" "mcp_ec2" {
  name              = "/aws/ec2/rememberly-mcp"
  retention_in_days = 7

  tags = {
    Name        = "rememberly-mcp-ec2-logs"
    Environment = var.environment
    Project     = "rememberly"
  }
}
