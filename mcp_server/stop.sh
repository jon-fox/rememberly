#!/bin/bash

echo "Stopping container..."
docker stop rememberly-mcp

echo "Removing container..."
docker rm rememberly-mcp

echo "Container stopped and removed"
