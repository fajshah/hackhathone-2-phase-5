"""
Authentication API endpoints for the Todo AI Chatbot.
Handles user registration, login, and authentication.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from ..auth import AuthService, get_current_user
from ..models.user import User
from ..database import get_session
from sqlmodel import Session, select
from ..services.task_service import task_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models for request/response
class LoginRequest(BaseModel):
    """
    Request model for login endpoint.
    """
    email: str
    password: str


class SignupRequest(BaseModel):
    """
    Request model for signup endpoint.
    """
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AuthResponse(BaseModel):
    """
    Response model for auth endpoints.
    """
    token: str
    user: dict
    success: bool


class UserResponse(BaseModel):
    """
    Response model for user info.
    """
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    User login endpoint.

    Authenticates a user and returns a JWT token.

    Args:
        request: LoginRequest containing email and password
        session: Database session for database operations

    Returns:
        AuthResponse with JWT token and user information
    """
    logger.info(f"Login attempt for user: {request.email}")

    try:
        # In a real implementation, you would fetch the user from the database
        # and verify the password. For now, we'll simulate a basic check.

        # Find user by email
        statement = select(User).where(User.email == request.email)
        user = session.exec(statement).first()

        if not user or not AuthService.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        # Create access token
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        token = AuthService.create_access_token(data=token_data)

        # Prepare user response
        user_response = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }

        logger.info(f"Successfully logged in user: {user.id}")

        return AuthResponse(
            token=token,
            user=user_response,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during login"
        )


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    User registration endpoint.

    Creates a new user account and returns a JWT token.

    Args:
        request: SignupRequest containing email, password, and optional first/last name
        session: Database session for database operations

    Returns:
        AuthResponse with JWT token and user information
    """
    logger.info(f"Signup attempt for email: {request.email}")

    try:
        # Check if user already exists
        statement = select(User).where(User.email == request.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash the password
        hashed_password = AuthService.get_password_hash(request.password)

        # Create new user
        new_user = User(
            email=request.email,
            hashed_password=hashed_password,
            first_name=request.first_name,
            last_name=request.last_name
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Create access token
        token_data = {
            "sub": str(new_user.id),
            "email": new_user.email
        }
        token = AuthService.create_access_token(data=token_data)

        # Prepare user response
        user_response = {
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name
        }

        logger.info(f"Successfully created user: {new_user.id}")

        return AuthResponse(
            token=token,
            user=user_response,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during signup"
        )


@router.get("/me", response_model=UserResponse)
async def get_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.

    Returns the authenticated user's information.

    Args:
        current_user: The authenticated user making the request

    Returns:
        UserResponse with user information
    """
    logger.info(f"Getting user info for user: {current_user.id}")

    try:
        user_response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name
        )

        logger.info(f"Successfully retrieved user info for: {current_user.id}")
        return user_response

    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving user information"
        )


logger.info("Authentication API endpoints registered successfully")