"""
Script to create a default user for local development
"""
import sys
import os
import uuid
from datetime import datetime

# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.database import get_session
from backend.src.models.user import User
from backend.src.auth import AuthService
from sqlmodel import select

def create_default_user():
    print("Creating default user for local development...")
    
    try:
        # Create a session
        session_gen = get_session()
        session = next(session_gen)
        
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if existing_user:
            print(f"Admin user already exists: {existing_user.email}")
            session.close()
            return
        
        # Hash the password
        hashed_password = AuthService.get_password_hash("password123")
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password=hashed_password,
            first_name="Admin",
            last_name="User",
            uuid=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print(f"Successfully created admin user: {admin_user.email}")
        print("Email: admin@example.com")
        print("Password: password123")
        
        session.close()
        print("Default user created successfully!")
        
    except Exception as e:
        print(f"Error creating default user: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_default_user()