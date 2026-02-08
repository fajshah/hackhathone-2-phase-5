"""
Database setup module for the Todo AI Chatbot.
Handles database connections and session management using SQLModel.
"""
from sqlmodel import create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
import logging

# Import settings
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database engine
# Using PostgreSQL for production, SQLite for development/testing
if settings.DATABASE_URL.startswith("postgresql"):
    # Production PostgreSQL setup
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_pre_ping=True,   # Verify connections before use
        pool_recycle=300,     # Recycle connections every 5 minutes
    )
else:
    # Development SQLite setup
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )

def get_session():
    """
    Generator function to provide database sessions.
    Ensures proper cleanup after each session.
    """
    with Session(engine) as session:
        yield session

# Optional: Add event listener to log SQL queries in development
if settings.DEBUG:
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        logger.debug(f"Executing SQL: {statement}")
        if parameters:
            logger.debug(f"With parameters: {parameters}")

def init_db():
    """
    Initialize the database by creating all tables.
    This should be called when starting the application.
    """
    from .models.user import User
    from .models.task import Task
    from .models.conversation import Conversation
    from .models.message import Message

    # Create all tables defined in the models
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")

# Initialize the database when this module is imported (only in main app context)
# Skip initialization during testing to avoid database connection issues
import os
if os.getenv("TESTING") != "1":
    init_db()