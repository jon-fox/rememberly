#!/bin/bash
# Build script for Lambda authorizer Docker image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="${IMAGE_NAME:-rememberly-authorizer}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "Building Lambda authorizer Docker image..."
echo "Image: $IMAGE_NAME:$IMAGE_TAG"

cd "$SCRIPT_DIR"

# Build the Docker image
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

echo "Build complete: $IMAGE_NAME:$IMAGE_TAG"
