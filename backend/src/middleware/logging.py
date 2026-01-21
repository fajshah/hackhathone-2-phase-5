"""
Logging middleware for the Todo AI Chatbot backend.
Logs incoming requests and outgoing responses for debugging and monitoring.
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests and outgoing responses.
    Logs request method, path, status code, response time, and basic user info.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request start
        start_time = time.time()

        # Get client IP
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"

        # Log request details
        logger.info(
            f"REQUEST_START | "
            f"method={request.method} | "
            f"path={request.url.path} | "
            f"client={client_host}:{client_port} | "
            f"user_agent={request.headers.get('user-agent', 'unknown')}"
        )

        try:
            # Process the request
            response = await call_next(request)

            # Calculate response time
            process_time = time.time() - start_time

            # Log response details
            logger.info(
                f"REQUEST_END | "
                f"status_code={response.status_code} | "
                f"process_time={process_time:.4f}s | "
                f"path={request.url.path}"
            )

            # Add process time to response headers
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # Calculate response time even for exceptions
            process_time = time.time() - start_time

            # Log exception
            logger.error(
                f"REQUEST_ERROR | "
                f"exception={str(e)} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"process_time={process_time:.4f}s"
            )

            # Re-raise the exception to be handled by error handlers
            raise