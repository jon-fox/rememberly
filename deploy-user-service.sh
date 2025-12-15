#!/bin/bash
# Build and deploy user service Lambda

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "====================================="
echo "User Service Lambda Deployment"
echo "====================================="
echo ""

# Step 1: Build and push Docker image
echo "Step 1: Building and pushing Docker image..."
cd "$SCRIPT_DIR/user_service"
chmod +x build.sh deploy.sh
./deploy.sh

echo ""
echo "Step 2: Updating Lambda function..."
cd "$SCRIPT_DIR/infra"

# Get the image URI
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/rememberly-user-service:latest"

# Update Lambda function with new image
echo "Updating Lambda function with image: ${IMAGE_URI}"
aws lambda update-function-code \
    --function-name rememberly-user-service \
    --image-uri "${IMAGE_URI}" \
    --region ${AWS_REGION}

echo ""
echo "✓ User service Lambda deployed successfully!"
echo ""
echo "Function: rememberly-user-service"
echo "Image: ${IMAGE_URI}"
