"""Authentication middleware for user lookup and validation.

This middleware enriches the user context with data from DynamoDB.
Users are validated based on X-User-Id header from Cloudflare Worker.
"""

import logging
import json
from typing import Any
from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
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

        user_id = None
        email = None
        user_data = None
        user_validated = False

        # Check for X-User-Id header from Cloudflare Worker
        # Access headers from ASGI scope
        try:
            if hasattr(context, 'scope') and 'headers' in context.scope:
                headers = dict(context.scope['headers'])
                # Headers are bytes in ASGI
                x_user_id = headers.get(b'x-user-id')
                if x_user_id:
                    user_id = x_user_id.decode('utf-8')
                    user_validated = True
                    logger.info(f"User ID from Cloudflare header: {user_id}")
                    
                    # Fetch user data from cache or DynamoDB
                    user_data = user_cache.get(user_id)
                    if user_data is None:
                        try:
                            user_data = users.get_user(user_id)
                            if user_data:
                                user_cache.set(user_id, user_data)
                                email = user_data.get('email')
                        except Exception as e:
                            logger.debug(f"Could not retrieve user data from DynamoDB: {str(e)}")
        except Exception as e:
            logger.error(f"Could not extract X-User-Id header: {str(e)}")

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
