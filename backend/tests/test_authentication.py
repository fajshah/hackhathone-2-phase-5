"""
Test suite for authentication functionality in the Todo AI Chatbot.
Tests user registration, login, and protected endpoints.
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from src.database import get_session
from src.main import app
from src.models.user import User, UserRole
from src.auth import AuthService
from datetime import timedelta
import warnings


@pytest.fixture
def test_client():
    """Set up a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_db_session():
    """Set up an in-memory test database session."""
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


def test_user_registration(test_client, test_db_session):
    """Test user registration functionality."""
    # Register a new user
    response = test_client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User"
    })

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["first_name"] == "Test"
    assert data["user"]["last_name"] == "User"

    # Verify user was created in database
    user = test_db_session.exec(select(User).where(User.email == "test@example.com")).first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.hashed_password is not None
    assert user.role == UserRole.USER


def test_user_login_success(test_client, test_db_session):
    """Test successful user login."""
    # First register a user
    register_response = test_client.post("/api/auth/signup", json={
        "email": "login@test.com",
        "password": "password123",
        "first_name": "Login",
        "last_name": "Test"
    })

    assert register_response.status_code == 200

    # Then try to log in
    login_response = test_client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "password123"
    })

    assert login_response.status_code == 200

    data = login_response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "login@test.com"


def test_user_login_failure_wrong_password(test_client, test_db_session):
    """Test user login with wrong password."""
    # First register a user
    register_response = test_client.post("/api/auth/signup", json={
        "email": "wrongpass@test.com",
        "password": "password123",
        "first_name": "Wrong",
        "last_name": "Pass"
    })

    assert register_response.status_code == 200

    # Try to log in with wrong password
    login_response = test_client.post("/api/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "wrongpassword"
    })

    assert login_response.status_code == 401
    data = login_response.json()
    assert "Incorrect email or password" in data["detail"]


def test_user_login_failure_nonexistent_user(test_client):
    """Test user login with nonexistent user."""
    login_response = test_client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "any_password"
    })

    assert login_response.status_code == 401
    data = login_response.json()
    assert "Incorrect email or password" in data["detail"]


def test_get_user_info_authenticated(test_client, test_db_session):
    """Test getting user info with valid authentication."""
    # Register and login a user
    register_response = test_client.post("/api/auth/signup", json={
        "email": "info@test.com",
        "password": "password123",
        "first_name": "Info",
        "last_name": "Test"
    })

    assert register_response.status_code == 200
    token = register_response.json()["token"]

    # Get user info with valid token
    headers = {"Authorization": f"Bearer {token}"}
    user_info_response = test_client.get("/api/auth/me", headers=headers)

    assert user_info_response.status_code == 200

    user_data = user_info_response.json()
    assert user_data["email"] == "info@test.com"
    assert user_data["first_name"] == "Info"
    assert user_data["last_name"] == "Test"


def test_get_user_info_unauthenticated(test_client):
    """Test getting user info without authentication."""
    # Try to get user info without token
    user_info_response = test_client.get("/api/auth/me")

    assert user_info_response.status_code == 403  # Or 401 depending on FastAPI settings


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


def test_duplicate_email_registration(test_client):
    """Test that registering with duplicate email fails."""
    # Register first user
    first_register = test_client.post("/api/auth/signup", json={
        "email": "duplicate@test.com",
        "password": "password123",
        "first_name": "Duplicate",
        "last_name": "First"
    })

    assert first_register.status_code == 200

    # Try to register second user with same email
    second_register = test_client.post("/api/auth/signup", json={
        "email": "duplicate@test.com",
        "password": "anotherpassword",
        "first_name": "Duplicate",
        "last_name": "Second"
    })

    assert second_register.status_code == 400
    data = second_register.json()
    assert "Email already registered" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__])