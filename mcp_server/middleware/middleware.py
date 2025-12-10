"""Authentication middleware for JWT token decoding and user lookup."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import jwt
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

        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    decoded_token = jwt.decode(
                        token, options={"verify_signature": False}
                    )
                    user_id = decoded_token.get("sub")
                    email = decoded_token.get("email")

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
            except (ValueError, jwt.DecodeError) as e:
                logger.debug(f"Auth failed: {str(e)}")

        user_context = UserContext(
            user_id=user_id,
            email=email,
            user_data=user_data,
            user_validated=user_validated,
        )

        request.state.user_context = user_context
        set_user_context(user_context)

        return await call_next(request)
