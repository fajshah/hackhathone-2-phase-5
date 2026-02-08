import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.src.models.task import Task
from backend.src.services.task_repository import TaskRepository
from backend.src.services.task_service import TaskService

# Use SQLite for local development
DATABASE_URL = "sqlite+aiosqlite:///./todo_chatbot_local.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncSession:
    """
    Get async database session as a generator for dependency injection.
    """
    async with async_session_maker() as session:
        yield session

async def init_db():
    """
    Initialize database connection and create tables if they don't exist.
    """
    from backend.src.models.task import Task
    from backend.src.models.reminder import Reminder
    from backend.src.models.session import UserSession

    # Import models to register them
    from sqlalchemy import text

    async with engine.begin() as conn:
        # For SQLite, we need to create tables manually or use reflection
        # Create the database file and tables
        pass

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Task.metadata.create_all)

async def close_db():
    """
    Close the database engine.
    """
    await engine.dispose()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown.
    """
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully")

    yield  # This is where the application runs

    print("Closing database connection...")
    await close_db()
    print("Database connection closed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Todo Chatbot API - Local Development",
    description="API for managing tasks in the cloud-native todo chatbot system (Local SQLite version)",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
from backend.src.api.health_routes import router as health_router
from backend.src.api.task_routes import router as task_router
from backend.src.api.chat_routes import router as chat_router
from backend.src.api.reminder_routes import router as reminder_router

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(task_router, prefix="/api/v1", tags=["tasks"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(reminder_router, prefix="/api/v1", tags=["reminders"])

@app.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Todo Chatbot API (Local Development Version)!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "timestamp": "2026-02-06T10:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "temp_backend_runner:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Turn off in production
    )