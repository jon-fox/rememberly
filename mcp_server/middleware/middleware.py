"""Authentication middleware for user lookup and validation.

This middleware enriches the user context with data from DynamoDB.
Users are validated based on X-User-Id header from Google OAuth authentication.
"""

import logging
import json
from typing import Any
from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
from cache import user_cache
from db import users
from models import UserContext

logger = logging.getLogger(__name__)


class AuthMiddleware(Middleware):
    """FastMCP middleware for authentication and user context enrichment."""

    async def on_message(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log all MCP messages and enrich user context."""

        # Log the incoming request
        logger.info(f"[MIDDLEWARE] Processing {context.method} from {context.source}")

        user_id = None
        email = None
        user_data = None
        user_validated = False

        # Check for X-User-Id header from Google OAuth authentication
        # Access headers from ASGI scope
        try:
            logger.info(f"[MIDDLEWARE] Checking for headers in context")
            logger.info(f"[MIDDLEWARE] Context attributes: {dir(context)}")
            if hasattr(context, "scope") and "headers" in context.scope:
                headers = dict(context.scope["headers"])
                logger.info(f"[MIDDLEWARE] Found {len(headers)} headers")
                logger.info(
                    f"[MIDDLEWARE] Scope path: {context.scope.get('path', 'N/A')}"
                )
                logger.info(
                    f"[MIDDLEWARE] Scope method: {context.scope.get('method', 'N/A')}"
                )

                # Log all headers for debugging (without sensitive values)
                for key, value in headers.items():
                    header_name = key.decode("utf-8") if isinstance(key, bytes) else key
                    logger.info(f"[MIDDLEWARE] Header: {header_name}")

                # Headers are bytes in ASGI
                x_user_id = headers.get(b"x-user-id")
                if x_user_id:
                    user_id = x_user_id.decode("utf-8")
                    user_validated = True
                    logger.info(
                        f"[MIDDLEWARE] User ID from Google OAuth header: {user_id}"
                    )
                else:
                    logger.warning(f"[MIDDLEWARE] No X-User-Id header found in request")

                    # Fetch user data from cache or DynamoDB
                    logger.info(f"[MIDDLEWARE] Fetching user data for {user_id}")
                    user_data = user_cache.get(user_id)
                    if user_data is None:
                        logger.info(
                            f"[MIDDLEWARE] User not in cache, querying DynamoDB"
                        )
                        try:
                            user_data = users.get_user(user_id)
                            if user_data:
                                logger.info(
                                    f"[MIDDLEWARE] Found user in DynamoDB, caching"
                                )
                                user_cache.set(user_id, user_data)
                                email = user_data.get("email")
                            else:
                                logger.warning(
                                    f"[MIDDLEWARE] User {user_id} not found in DynamoDB"
                                )
                        except Exception as e:
                            logger.error(
                                f"[MIDDLEWARE] Error retrieving user data from DynamoDB: {str(e)}"
                            )
                    else:
                        logger.info(f"[MIDDLEWARE] User found in cache")
                        email = user_data.get("email") if user_data else None
            else:
                logger.warning(f"[MIDDLEWARE] No scope or headers in context")
        except Exception as e:
            logger.error(
                f"[MIDDLEWARE] Exception extracting X-User-Id header: {str(e)}"
            )
            import traceback

            logger.error(f"[MIDDLEWARE] Traceback: {traceback.format_exc()}")

        logger.info(
            f"[MIDDLEWARE] Final user_context: authenticated={user_validated}, user_id={user_id}, email={email}"
        )
        user_context = UserContext(
            user_id=user_id,
            email=email,
            user_data=user_data,
            user_validated=user_validated,
        )

        # User context is created but not stored globally since FastMCP handles auth
        logger.info(f"[MIDDLEWARE] User context created: {user_context}")

        logger.info(f"[MIDDLEWARE] Calling next handler for {context.method}")
        result = await call_next(context)
        logger.info(f"[MIDDLEWARE] Completed {context.method}")

        return result
