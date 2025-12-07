"""
Lambda Authorizer for MCP Gateway
Validates API keys stored in AWS Secrets Manager
"""
import json
import os
from typing import Dict, Any

# boto3 is available in Lambda runtime by default
import boto3

secretsmanager = boto3.client('secretsmanager')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Authorizer Lambda handler that validates API keys
    
    Expected event structure:
    {
        "headers": {
            "x-api-key": "api-key-value"
        },
        "requestContext": {...}
    }
    """
    print(f"Authorizer invoked with event: {json.dumps(event)}")
    
    try:
        # Extract API key from headers
        headers = event.get('headers', {})
        api_key = headers.get('x-api-key') or headers.get('X-API-Key')
        
        if not api_key:
            print("No API key provided in request headers")
            return generate_policy('user', 'Deny', event.get('methodArn', '*'))
        
        # Get valid API keys from Secrets Manager
        secret_name = os.environ.get('SECRET_NAME', 'rememberly-mcp-api-keys')
        
        try:
            response = secretsmanager.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response['SecretString'])
            valid_api_keys = secret_data.get('api_keys', {})
        except Exception as e:
            print(f"Error retrieving secrets: {str(e)}")
            return generate_policy('user', 'Deny', event.get('methodArn', '*'))
        
        # Validate the API key
        if api_key in valid_api_keys.values():
            print("Valid API key provided")
            # Find the key ID for the API key
            principal_id = next(
                (key_id for key_id, key_val in valid_api_keys.items() if key_val == api_key),
                'authenticated-user'
            )
            return generate_policy(principal_id, 'Allow', event.get('methodArn', '*'))
        else:
            print("Invalid API key provided")
            return generate_policy('user', 'Deny', event.get('methodArn', '*'))
            
    except Exception as e:
        print(f"Authorization error: {str(e)}")
        return generate_policy('user', 'Deny', event.get('methodArn', '*'))


def generate_policy(principal_id: str, effect: str, resource: str) -> Dict[str, Any]:
    """
    Generate an IAM policy for the gateway
    """
    auth_response = {
        'principalId': principal_id
    }
    
    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
        auth_response['policyDocument'] = policy_document
    
    # Optional: Add context data to pass to the backend
    auth_response['context'] = {
        'userId': principal_id,
        'authorized': str(effect == 'Allow').lower()
    }
    
    return auth_response
