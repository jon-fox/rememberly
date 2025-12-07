#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="app-ecr-repo"

echo "WARNING: This will delete ALL images in ${ECR_REPOSITORY}"
read -p "Are you sure? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Deleting all images from ${ECR_REPOSITORY}..."

aws ecr batch-delete-image \
    --repository-name ${ECR_REPOSITORY} \
    --region ${AWS_REGION} \
    --image-ids "$(aws ecr list-images --repository-name ${ECR_REPOSITORY} --region ${AWS_REGION} --query 'imageIds[*]' --output json)" \
    || true

# Delete any remaining manifest lists
aws ecr batch-delete-image \
    --repository-name ${ECR_REPOSITORY} \
    --region ${AWS_REGION} \
    --image-ids "$(aws ecr list-images --repository-name ${ECR_REPOSITORY} --region ${AWS_REGION} --query 'imageIds[*]' --output json)" \
    || true

echo "All images deleted from ${ECR_REPOSITORY}"
