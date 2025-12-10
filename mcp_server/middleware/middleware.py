"""Authentication middleware for JWT token decoding and user lookup."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt
from cache import user_cache
from db import users

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/healthz", "/"]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401, content={"error": "Missing Authorization header"}
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=401, content={"error": "Invalid authorization scheme"}
                )
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid Authorization header format"},
            )

        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return JSONResponse(
                status_code=401, content={"error": "Invalid token format"}
            )

        user_id = decoded_token.get("sub")
        user_data = user_cache.get(user_id)

        if user_data is None:
            try:
                user_data = users.get_user(user_id)
                if user_data:
                    user_cache.set(user_id, user_data)
            except Exception as e:
                logger.error(f"Error retrieving user from DynamoDB: {str(e)}")

        request.state.user_id = user_id
        request.state.token = decoded_token
        request.state.email = decoded_token.get("email")
        request.state.user_data = user_data

        return await call_next(request)
