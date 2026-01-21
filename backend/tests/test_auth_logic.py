"""
Simple test for authentication functionality in the Todo AI Chatbot.
Tests just the core authentication logic without database initialization.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import timedelta
from src.auth import AuthService
from src.models.user import User, UserRole
from passlib.context import CryptContext
import jwt
from src.config import settings


def test_password_hashing():
    """Test that password hashing works correctly."""
    password = "mysecretpassword"

    # Hash the password
    hashed = AuthService.get_password_hash(password)

    # Verify the password
    assert AuthService.verify_password(password, hashed)

    # Verify a wrong password fails
    assert not AuthService.verify_password("wrongpassword", hashed)


def test_jwt_token_generation():
    """Test JWT token generation and decoding."""
    # Create token data
    token_data = {
        "sub": "123",
        "email": "test@example.com"
    }

    # Generate token
    token = AuthService.create_access_token(data=token_data, expires_delta=timedelta(minutes=15))

    # Decode token
    decoded = AuthService.decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["email"] == "test@example.com"


def test_jwt_token_expiration():
    """Test JWT token expiration."""
    # Create token that expires immediately
    token = AuthService.create_access_token(data={"sub": "123"}, expires_delta=timedelta(seconds=1))

    # Wait for expiration
    import time
    time.sleep(2)

    # Try to decode expired token
    decoded = AuthService.decode_access_token(token)

    # Token should be expired and return None
    assert decoded is None


def test_invalid_token():
    """Test decoding an invalid token."""
    invalid_token = "invalid.token.string"

    decoded = AuthService.decode_access_token(invalid_token)

    assert decoded is None


def test_user_model_creation():
    """Test creating a user model."""
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        hashed_password="some_hashed_password"
    )

    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role == UserRole.USER
    assert user.hashed_password == "some_hashed_password"
    assert user.is_active is True  # Default value
    assert user.is_verified is False  # Default value


if __name__ == "__main__":
    pytest.main([__file__])