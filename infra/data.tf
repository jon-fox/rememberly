# Data sources for existing AWS resources

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get all subnets in the default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Get subnet details
data "aws_subnet" "default" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

# Get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}
