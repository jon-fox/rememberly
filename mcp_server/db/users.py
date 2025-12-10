"""User data operations with DynamoDB."""

import logging
import os
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

_dynamodb = None
_table = None


def _get_table():
    global _dynamodb, _table
    if _table is None:
        table_name = os.getenv("DYNAMODB_TABLE")
        if not table_name:
            raise ValueError("DYNAMODB_TABLE environment variable not set")
        _dynamodb = boto3.resource("dynamodb")
        _table = _dynamodb.Table(table_name)
    return _table


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Look up user data from DynamoDB.

    Args:
        user_id: The user ID (sub from JWT)

    Returns:
        User data from DynamoDB or None if not found
    """
    try:
        table = _get_table()
        response = table.get_item(Key={"pk": f"USER#{user_id}", "sk": "PROFILE"})

        item = response.get("Item")
        if item:
            logger.info(f"Found user in DynamoDB: {user_id}")
            return item
        else:
            logger.info(f"User not found in DynamoDB: {user_id}")
            return None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"DynamoDB error ({error_code}): {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error querying DynamoDB: {str(e)}")
        raise
