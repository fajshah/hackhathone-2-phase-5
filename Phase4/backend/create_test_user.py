"""
Script to create a test user for the Todo AI Chatbot application
"""
import sys
import os
import uuid
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.core.auth import get_password_hash

def create_test_user():
    print("Creating test user...")

    try:
        # Create a session
        with Session(engine) as session:
            # Check if user already exists
            existing_user = session.exec(select(User).where(User.email == "test@example.com")).first()
            if existing_user:
                print(f"Test user already exists: {existing_user.email}")
                return existing_user

            # Hash the password
            hashed_password = get_password_hash("password123")

            # Create test user
            test_user = User(
                email="test@example.com",
                name="Test User",
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            print(f"Successfully created test user: {test_user.email}")
            print("Email: test@example.com")
            print("Password: password123")

            return test_user

    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user()