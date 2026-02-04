"""
Simple test for authentication functionality in the Todo AI Chatbot.
Tests just the core authentication functions in isolation.
"""
import pytest
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import os


# Replicate the core authentication functions in isolation
class IsolatedAuthService:
    """
    Isolated service class for testing authentication functions without database dependencies.
    """

    # Password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        """
        return IsolatedAuthService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Generate a hash for a plain password.
        """
        return IsolatedAuthService.pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token with optional expiration.
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default expiration: 15 minutes
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})

        # Use a test secret for testing
        secret = "test-secret-for-authentication-testing"
        algorithm = "HS256"

        encoded_jwt = jwt.encode(
            to_encode,
            secret,
            algorithm=algorithm
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str, secret: str = "test-secret-for-authentication-testing") -> Optional[dict]:
        """
        Decode a JWT token and return its payload.
        """
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"]
            )
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
            # Token has expired or is invalid
            return None


def test_password_hashing():
    """Test that password hashing works correctly."""
    password = "mysecretpassword"

    # Hash the password
    hashed = IsolatedAuthService.get_password_hash(password)

    # Verify the password
    assert IsolatedAuthService.verify_password(password, hashed)

    # Verify a wrong password fails
    assert not IsolatedAuthService.verify_password("wrongpassword", hashed)


def test_jwt_token_generation():
    """Test JWT token generation and decoding."""
    # Create token data
    token_data = {
        "sub": "123",
        "email": "test@example.com"
    }

    # Generate token
    token = IsolatedAuthService.create_access_token(data=token_data, expires_delta=timedelta(minutes=15))

    # Decode token
    decoded = IsolatedAuthService.decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["email"] == "test@example.com"


def test_jwt_token_expiration():
    """Test JWT token expiration."""
    # Create token that expires immediately
    token = IsolatedAuthService.create_access_token(data={"sub": "123"}, expires_delta=timedelta(seconds=1))

    # Wait for expiration
    import time
    time.sleep(2)

    # Try to decode expired token
    decoded = IsolatedAuthService.decode_access_token(token)

    # Token should be expired and return None
    assert decoded is None


def test_invalid_token():
    """Test decoding an invalid token."""
    invalid_token = "invalid.token.string"

    decoded = IsolatedAuthService.decode_access_token(invalid_token)

    assert decoded is None


if __name__ == "__main__":
    pytest.main([__file__])