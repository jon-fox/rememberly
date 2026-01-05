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
s3_client = boto3.client("s3")


def get_table():
    """Get DynamoDB table reference."""
    table_name = os.getenv("DYNAMODB_TABLE")
    if not table_name:
        raise ValueError("DYNAMODB_TABLE environment variable not set")
    return dynamodb.Table(table_name)


def create_or_update_user(
    user_id: str, email: str, username: str = None
) -> Dict[str, Any]:
    """Create a new user or update existing user if data has changed."""
    table = get_table()
    timestamp = datetime.utcnow().isoformat()

    # Check if user already exists
    try:
        response = table.get_item(Key={"pk": f"USER#{user_id}", "sk": "PROFILE"})

        existing_user = response.get("Item")

        if existing_user:
            # Check if any data has changed
            needs_update = False
            updates = {}

            if existing_user.get("email") != email:
                updates["email"] = email
                needs_update = True

            if username and existing_user.get("username") != username:
                updates["username"] = username
                needs_update = True

            if needs_update:
                # Update only changed fields
                updates["updated_at"] = timestamp

                update_expression = "SET " + ", ".join(
                    [f"#{k} = :{k}" for k in updates.keys()]
                )
                expression_attribute_names = {f"#{k}": k for k in updates.keys()}
                expression_attribute_values = {f":{k}": v for k, v in updates.items()}

                table.update_item(
                    Key={"pk": f"USER#{user_id}", "sk": "PROFILE"},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                )
                logger.info(
                    f"Updated user in DynamoDB: {user_id}, changes: {list(updates.keys())}"
                )
            else:
                logger.info(
                    f"User {user_id} already exists with same data, skipping update"
                )

            return existing_user

    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    # User doesn't exist, create new user
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

    # Create default bucket in S3
    # Storage key format: {user_email}/{bucket}/{key}
    storage_bucket = os.getenv("STORAGE_BUCKET")
    if storage_bucket:
        try:
            # Create the default bucket path/folder in S3
            s3_key = f"{email}/default/"

            s3_client.put_object(Bucket=storage_bucket, Key=s3_key, Body=b"")
            logger.info(f"Created default bucket path in S3 for user: {email}")
        except ClientError as e:
            logger.error(f"Failed to create default bucket in S3 for {email}: {str(e)}")
            # Don't fail user creation if bucket creation fails
    else:
        logger.warning(
            "STORAGE_BUCKET environment variable not set, skipping S3 bucket creation"
        )

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

        # Create or update user (only if data changed)
        user_data = create_or_update_user(user_id, email, username)

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"message": "User created successfully", "user": user_data}
            ),
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
