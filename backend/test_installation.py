"""
Test script to verify that the backend requirements have been installed correctly.
"""

def test_imports():
    """Test importing the main packages."""
    try:
        import flask
        print(f"[OK] Flask version: {flask.__version__}")
        
        import flask_cors
        print(f"[OK] Flask-CORS version: {flask_cors.__version__}")
        
        import sqlalchemy
        print(f"[OK] SQLAlchemy version: {sqlalchemy.__version__}")
        
        import alembic
        print(f"[OK] Alembic version: {alembic.__version__}")
        
        import pytest
        print(f"[OK] Pytest version: {pytest.__version__}")
        
        import dotenv
        print("[OK] python-dotenv imported successfully")
        
        import flask_migrate
        print("[OK] Flask-Migrate imported successfully")
        
        import flask_sqlalchemy
        print("[OK] Flask-SQLAlchemy imported successfully")
        
        import structlog
        print("[OK] Structlog imported successfully")
        
        import marshmallow
        print("[OK] Marshmallow imported successfully")
        
        import flask_login
        print("[OK] Flask-Login imported successfully")
        
        import bcrypt
        print("[OK] Bcrypt imported successfully")
        
        import dateutil
        print("[OK] python-dateutil imported successfully")
        
        import requests
        print(f"[OK] Requests version: {requests.__version__}")
        
        import celery
        print(f"[OK] Celery version: {celery.__version__}")
        
        import redis
        print(f"[OK] Redis version: {redis.__version__}")
        
        print("\nAll required packages have been successfully installed!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend package installations...\n")
    success = test_imports()
    
    if success:
        print("\n[SUCCESS] Installation verification completed successfully!")
    else:
        print("\n[FAILED] Some packages failed to import.")