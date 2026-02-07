"""
Health check utilities for the Todo AI Chatbot backend.
Provides database connectivity and service health checks.
"""
from typing import Dict, Any
from sqlalchemy import text
from ..database import engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_database_health() -> Dict[str, Any]:
    """
    Check the health of the database connection.
    Returns a dictionary with health status and details.
    """
    try:
        # Execute a simple query to test database connectivity
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            # Fetch the result to ensure the query executed successfully
            result.fetchone()

        return {
            "status": "healthy",
            "component": "database",
            "details": "Successfully connected to database"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "component": "database",
            "details": f"Database connection failed: {str(e)}"
        }

async def check_app_health() -> Dict[str, Any]:
    """
    Check the overall health of the application.
    Returns a dictionary with health status and details for all components.
    """
    # Check database health
    db_health = await check_database_health()

    # Add other health checks as needed
    # For now, we just have the database check

    overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"

    return {
        "status": overall_status,
        "checks": {
            "database": db_health
        },
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }