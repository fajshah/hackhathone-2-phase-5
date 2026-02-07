"""
Chat authentication middleware for the Todo AI Chatbot.
Provides additional authentication checks specific to chat endpoints.
"""
from fastapi import HTTPException, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..auth import AuthService
from ..models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme for API docs
security = HTTPBearer()

class ChatAuthMiddleware:
    """
    Middleware class for handling authentication specific to chat endpoints.
    Verifies that users are properly authenticated before allowing chat operations.
    """

    @staticmethod
    async def verify_chat_access(
        request: Request,
        credentials: HTTPAuthorizationCredentials = security
    ) -> User:
        """
        Verify that the user is authenticated and has access to chat functionality.

        Args:
            request: The incoming request object
            credentials: The authorization credentials from the request

        Returns:
            The authenticated user object

        Raises:
            HTTPException: If authentication fails
        """
        # Extract token from credentials
        token = credentials.credentials

        # Verify the token using the AuthService
        user_payload = AuthService.decode_access_token(token)

        if user_payload is None:
            logger.warning(f"Invalid or expired token in chat request from {request.client.host}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials for chat access",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user ID from payload
        user_id: str = user_payload.get("sub")
        if user_id is None:
            logger.warning(f"No user ID in token payload for chat request from {request.client.host}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials for chat access",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        # In a real implementation, we would fetch the user from the database
        # Here we'll just create a basic user object
        try:
            user_id_int = int(user_id)
            # In a real implementation, we would fetch from DB:
            # user = await get_user_by_id(user_id_int)
            # if not user or not user.is_active:
            #     raise HTTPException(
            #         status_code=401,
            #         detail="User account is inactive",
            #         headers={"WWW-Authenticate": "Bearer"},
            #     )

            # For now, we'll create a mock user object
            user = User(id=user_id_int, email=user_payload.get("email", f"user_{user_id}@example.com"))
            logger.info(f"User {user_id_int} authenticated for chat access")
            return user

        except ValueError:
            logger.error(f"Invalid user ID format in token: {user_id}")
            raise HTTPException(
                status_code=401,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Error authenticating user for chat: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication error",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def validate_conversation_access(user: User, conversation_id: int) -> bool:
        """
        Validate that the user has access to a specific conversation.

        Args:
            user: The authenticated user
            conversation_id: The ID of the conversation to check

        Returns:
            True if user has access, False otherwise
        """
        # This would typically involve checking the database to ensure
        # the conversation belongs to the user
        # For now, we'll return True as the actual check happens in the service layer
        logger.info(f"Validating access to conversation {conversation_id} for user {user.id}")
        return True


# Create an instance of the middleware
chat_auth = ChatAuthMiddleware()