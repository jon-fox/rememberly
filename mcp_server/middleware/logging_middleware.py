"""HTTP request/response logging middleware for debugging OAuth flow."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """Log incoming requests and outgoing responses."""

        # Log request details
        logger.info(f"[HTTP] --> {request.method} {request.url.path}")

        # Log query parameters
        if request.query_params:
            logger.info(f"[HTTP] Query params: {dict(request.query_params)}")

        # Log important headers (excluding sensitive ones)
        important_headers = [
            "authorization",
            "content-type",
            "user-agent",
            "x-user-id",
            "referer",
            "origin",
        ]
        for header_name in important_headers:
            header_value = request.headers.get(header_name)
            if header_value:
                # Mask authorization tokens
                if header_name == "authorization" and len(header_value) > 20:
                    masked_value = f"{header_value[:10]}...{header_value[-10:]}"
                    logger.info(f"[HTTP] Header {header_name}: {masked_value}")
                else:
                    logger.info(f"[HTTP] Header {header_name}: {header_value}")

        # Log client IP
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"[HTTP] Client IP: {client_ip}")

        # Process the request
        try:
            response = await call_next(request)

            # Log response
            logger.info(
                f"[HTTP] <-- {response.status_code} for {request.method} {request.url.path}"
            )

            # Log response headers for redirects
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get("location", "N/A")
                logger.info(f"[HTTP] Redirect location: {location}")

            return response

        except Exception as e:
            logger.error(f"[HTTP] Exception during request: {str(e)}")
            logger.error(f"[HTTP] Request: {request.method} {request.url.path}")
            import traceback

            logger.error(f"[HTTP] Traceback: {traceback.format_exc()}")
            raise
