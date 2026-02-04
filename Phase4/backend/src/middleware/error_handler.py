"""
Error handling middleware for the Todo AI Chatbot backend.
Sets up centralized error handlers for the FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_error_handlers(app: FastAPI):
    """
    Set up centralized error handlers for the FastAPI application.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle HTTP exceptions.
        """
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle request validation errors.
        """
        logger.error(f"Validation Error: {exc.errors()} - Path: {request.url.path}")

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                    "status_code": 422
                }
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle general exceptions.
        """
        logger.error(f"General Exception: {str(exc)} - Path: {request.url.path}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An internal server error occurred",
                    "status_code": 500
                }
            }
        )

# Example of a custom exception for the Todo AI Chatbot
class TodoException(Exception):
    """
    Custom exception for todo-related errors.
    """
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TaskNotFoundException(TodoException):
    """
    Exception raised when a task is not found.
    """
    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} not found", 404)

class UserNotAuthorizedException(TodoException):
    """
    Exception raised when a user is not authorized to perform an action.
    """
    def __init__(self):
        super().__init__("User not authorized to perform this action", 403)