"""Lambda handler entry point for Rememberly MCP Server."""

import json
import base64
from typing import Any, Dict
from server import mcp


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for MCP server requests.
    
    Args:
        event: Lambda event containing the MCP request
        context: Lambda context object
        
    Returns:
        Response dict with statusCode and body
    """
    try:
        # Extract the MCP request from the event
        # Support both direct body and API Gateway format
        if "body" in event:
            if event.get("isBase64Encoded", False):
                body = base64.b64decode(event["body"]).decode("utf-8")
            else:
                body = event["body"]
            request_data = json.loads(body) if isinstance(body, str) else body
        else:
            request_data = event
        
        # Process the MCP request
        # The mcp instance handles the protocol internally
        response = mcp.handle_request(request_data)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps(response)
        }
    
    except json.JSONDecodeError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Invalid JSON in request",
                "details": str(e)
            })
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }
