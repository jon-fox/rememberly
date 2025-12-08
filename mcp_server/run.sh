#!/bin/bash
set -e

ACCOUNT_ID="381492150662"
REGION="us-east-1"
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/app-ecr-repo:latest"

echo "Authenticating with ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "Pulling image..."
docker pull --platform linux/amd64 $IMAGE_URI

echo "Running container on port 9000..."
docker run -d --platform linux/amd64 -p 9000:8080 \
  --name rememberly-mcp \
  -e STORAGE_BUCKET=rememberly-storage-prod \
  -e DYNAMODB_TABLE=rememberly-metadata-prod \
  -e SUPABASE_URL=https://ijyyifghxitisjbfnoxb.supabase.co \
  -e ENVIRONMENT=dev \
  -e IMAGE_VERSION=1 \
  $IMAGE_URI

echo "Container running. View logs: docker logs -f rememberly-mcp"
echo "Stop container: docker stop rememberly-mcp && docker rm rememberly-mcp"
