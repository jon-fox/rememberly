"""Authentication middleware for user lookup after JWT validation.

JWT signature validation is handled by FastMCP's JWTVerifier.
This middleware enriches the user context with data from DynamoDB.
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastmcp.server.dependencies import get_access_token
from cache import user_cache
from db import users
from models import UserContext
from services.tool_service import set_user_context

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/healthz", "/"]:
            return await call_next(request)

        user_id = None
        email = None
        user_data = None
        user_validated = False

        # Get validated access token from FastMCP auth
        try:
            access_token = get_access_token()
            if access_token and access_token.claims:
                user_id = access_token.claims.get("sub")
                email = access_token.claims.get("email")

                # Look up user in DynamoDB
                user_data = user_cache.get(user_id)
                if user_data is None:
                    try:
                        user_data = users.get_user(user_id)
                        if user_data:
                            user_cache.set(user_id, user_data)
                    except Exception as e:
                        logger.error(
                            f"Error retrieving user from DynamoDB: {str(e)}"
                        )

                user_validated = user_data is not None
        except Exception as e:
            logger.debug(f"Auth context retrieval failed: {str(e)}")

        user_context = UserContext(
            user_id=user_id,
            email=email,
            user_data=user_data,
            user_validated=user_validated,
        )

        request.state.user_context = user_context
        set_user_context(user_context)

        return await call_next(request)
