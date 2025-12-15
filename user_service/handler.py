"""User management Lambda handler - separate from MCP server."""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")


def get_table():
    """Get DynamoDB table reference."""
    table_name = os.getenv("DYNAMODB_TABLE")
    if not table_name:
        raise ValueError("DYNAMODB_TABLE environment variable not set")
    return dynamodb.Table(table_name)


def create_user(user_id: str, email: str, username: str = None) -> Dict[str, Any]:
    """Create a new user in DynamoDB."""
    table = get_table()
    timestamp = datetime.utcnow().isoformat()
    
    user_data = {
        "pk": f"USER#{user_id}",
        "sk": "PROFILE",
        "user_id": user_id,
        "email": email,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    
    if username:
        user_data["username"] = username
    
    table.put_item(Item=user_data)
    logger.info(f"Created user in DynamoDB: {user_id}")
    
    return user_data


def lambda_handler(event, context):
    """Lambda handler for user management operations."""
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Handle CORS preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }
    
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        email = body.get("email")
        username = body.get("username")
        
        # Validate required fields
        if not user_id or not email:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "user_id and email are required"}),
            }
        
        # Create user
        user_data = create_user(user_id, email, username)
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "message": "User created successfully",
                "user": user_data
            }),
        }
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": f"Database error: {str(e)}"}),
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
