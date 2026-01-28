#!/bin/bash
# Assume role and destroy Terraform resources

set -e

ROLE_ARN="arn:aws:iam::381492150662:role/terraform-dev"
SESSION_NAME="terraform-session-$(date +%s)"

echo "Assuming role: $ROLE_ARN"

# Get temporary credentials
CREDENTIALS=$(aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESSION_NAME" \
  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
  --output text)

# Parse credentials
AWS_ACCESS_KEY_ID=$(echo "$CREDENTIALS" | awk '{print $1}')
AWS_SECRET_ACCESS_KEY=$(echo "$CREDENTIALS" | awk '{print $2}')
AWS_SESSION_TOKEN=$(echo "$CREDENTIALS" | awk '{print $3}')

# Export credentials
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN

echo "Credentials exported. Running terraform destroy..."

# Run terraform destroy with tfvars file
cd "$(dirname "$0")"
terraform destroy -var-file="terraform.tfvars" "$@"
