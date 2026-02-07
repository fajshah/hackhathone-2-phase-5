"""
Database connection and session management for the todo chatbot system.
Uses NeonDB (PostgreSQL-compatible) for persistent storage.
"""
import os
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager


# Database configuration from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo_chatbot_local.db"  # Changed to SQLite for local development
)


# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    pool_pre_ping=True,
)


# Create async session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session as a generator for dependency injection.
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """
    Initialize database connection and create tables if they don't exist.
    """
    from .models.task import Task
    from .models.reminder import Reminder
    from .models.session import UserSession
    from .models.event_log import EventLog

    # Import the models to register them with SQLAlchemy
    # This will allow the tables to be created

    async with engine.begin() as conn:
        # Create tables (this would typically be handled by Alembic migrations in production)
        # For now, we'll create them directly
        await conn.run_sync(Task.metadata.create_all)


async def close_db():
    """
    Close the database engine.
    """
    await engine.dispose()