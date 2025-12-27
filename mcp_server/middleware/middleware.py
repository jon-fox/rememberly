"""Authentication middleware for user lookup and validation.

This middleware enriches the user context with data from DynamoDB.
Users are validated based on email from access token claims.
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

        # Log incoming request details
        auth_header = request.headers.get("authorization", "")
        has_bearer = auth_header.startswith("Bearer ")

        # Get request body if available
        body_bytes = await request.body()
        request_body = body_bytes.decode() if body_bytes else None

        # Rebuild request with body for downstream processing
        async def receive():
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive

        logger.info(
            f"Request: {request.method} {request.url.path} | Auth header present: {bool(auth_header)} | Bearer token: {has_bearer}"
        )
        logger.info(f"Request body: {request_body}")
        if has_bearer:
            logger.info(f"Full Bearer token: {auth_header}")

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

        request.state.user_context = user_context
        set_user_context(user_context)

        return await call_next(request)
