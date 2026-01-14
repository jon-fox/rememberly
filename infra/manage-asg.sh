#!/bin/bash
# Script to manage MCP Auto Scaling Group capacity

set -e

ASG_NAME="rememberly-mcp-asg"
REGION="us-east-1"

case "$1" in
  start)
    echo "Starting MCP server (setting desired capacity to 1)..."
    aws autoscaling set-desired-capacity \
      --auto-scaling-group-name "$ASG_NAME" \
      --desired-capacity 1 \
      --region "$REGION"
    echo "Desired capacity set to 1. Instance will launch shortly."
    echo "Monitor status: aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names $ASG_NAME --region $REGION"
    ;;
  
  stop)
    echo "Stopping MCP server (setting desired capacity to 0)..."
    aws autoscaling set-desired-capacity \
      --auto-scaling-group-name "$ASG_NAME" \
      --desired-capacity 0 \
      --region "$REGION"
    echo "Desired capacity set to 0. Instance will terminate shortly."
    ;;
  
  status)
    echo "Checking MCP Auto Scaling Group status..."
    aws autoscaling describe-auto-scaling-groups \
      --auto-scaling-group-names "$ASG_NAME" \
      --region "$REGION" \
      --query 'AutoScalingGroups[0].{DesiredCapacity:DesiredCapacity,CurrentCapacity:Instances[0].HealthStatus,Instances:Instances[*].[InstanceId,LifecycleState,HealthStatus]}' \
      --output table
    ;;
  
  *)
    echo "Usage: $0 {start|stop|status}"
    echo ""
    echo "Commands:"
    echo "  start  - Start MCP server by setting ASG desired capacity to 1"
    echo "  stop   - Stop MCP server by setting ASG desired capacity to 0"
    echo "  status - Check current ASG and instance status"
    exit 1
    ;;
esac
