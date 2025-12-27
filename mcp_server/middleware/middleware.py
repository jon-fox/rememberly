"""Authentication middleware for user lookup and validation.

This middleware enriches the user context with data from DynamoDB.
Users are validated based on email from access token claims.
"""

import logging
import json
from typing import Any
from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
from fastmcp.server.dependencies import get_access_token
from cache import user_cache
from db import users
from models import UserContext
from services.tool_service import set_user_context

logger = logging.getLogger(__name__)


class AuthMiddleware(Middleware):
    """FastMCP middleware for authentication and user context enrichment."""

    async def on_message(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log all MCP messages and enrich user context."""
        
        # Log the incoming request
        logger.info(f"Processing {context.method} from {context.source}")
        
        # Log the full request payload
        try:
            request_json = json.dumps(context.request, indent=2)
            logger.info(f"Request payload: {request_json}")
        except Exception as e:
            logger.warning(f"Could not serialize request: {e}")

        user_id = None
        email = None
        user_data = None
        user_validated = False

        try:
            access_token = get_access_token()
            logger.info(f"get_access_token() returned: {access_token is not None}")
            if access_token and access_token.claims:
                user_id = access_token.claims.get("sub")
                email = access_token.claims.get("email")
                user_validated = email is not None
                logger.info(
                    f"Token claims extracted: user_id={user_id}, email={email}, validated={user_validated}"
                )

                if user_id:
                    user_data = user_cache.get(user_id)
                    if user_data is None:
                        try:
                            user_data = users.get_user(user_id)
                            if user_data:
                                user_cache.set(user_id, user_data)
                        except Exception as e:
                            logger.debug(
                                f"Could not retrieve user data from DynamoDB: {str(e)}"
                            )
        except Exception as e:
            logger.warning(f"Auth context retrieval failed: {str(e)}")

        logger.info(
            f"Final user_context: authenticated={user_validated}, user_id={user_id}"
        )
        user_context = UserContext(
            user_id=user_id,
            email=email,
            user_data=user_data,
            user_validated=user_validated,
        )

        set_user_context(user_context)
        
        result = await call_next(context)
        
        logger.info(f"Completed {context.method}")
        return result
