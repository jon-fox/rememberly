"""Secrets Manager caching with TTL support."""

import json
import logging
from typing import Optional, Any
import boto3
from botocore.exceptions import ClientError
from . import user_cache

logger = logging.getLogger(__name__)

_client = boto3.client("secretsmanager", region_name="us-east-1")


def get_secret(secret_name: str, parse_json: bool = False) -> Optional[Any]:
    cached_value = user_cache.get(secret_name)
    if cached_value is not None:
        return cached_value

    try:
        response = _client.get_secret_value(SecretId=secret_name)
        secret_value = response.get("SecretString")

        if secret_value and parse_json:
            secret_value = json.loads(secret_value)

        if secret_value:
            user_cache.set(secret_name, secret_value)

        return secret_value

    except ClientError as e:
        logger.error(
            f"Error fetching secret {secret_name}: {e.response['Error']['Code']}"
        )
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching secret {secret_name}: {str(e)}")
        return None
