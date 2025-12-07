#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="381492150662"
ECR_REPOSITORY="app-ecr-repo"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="${1:-latest}"

echo "Building and pushing MCP Lambda image..."
echo "Registry: ${ECR_REGISTRY}"
echo "Repository: ${ECR_REPOSITORY}"
echo "Tag: ${IMAGE_TAG}"

# Login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build the Docker image
echo "Building Docker image..."
docker build --platform linux/amd64 -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} .

# Tag as latest as well
docker tag ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

# Push both tags
echo "Pushing image to ECR..."
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

echo "✓ Image pushed successfully!"
echo "Image URI: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
echo ""
echo "To deploy with Terraform, run:"
echo "cd ../infra && terraform apply -var=\"mcp_lambda_image_uri=${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}\""
