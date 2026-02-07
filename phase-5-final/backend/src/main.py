"""
Main FastAPI application for the todo chatbot system.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .database import init_db, close_db, get_async_session
from .services.task_repository import TaskRepository
from .services.task_service import TaskService


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown.
    """
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    yield  # This is where the application runs

    logger.info("Closing database connection...")
    await close_db()
    logger.info("Database connection closed")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Todo Chatbot API",
    description="API for managing tasks in the cloud-native todo chatbot system",
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
from .api.health_routes import router as health_router
from .api.task_routes import router as task_router
from .api.chat_routes import router as chat_router
from .api.reminder_routes import router as reminder_router


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
    return {"message": "Welcome to the Todo Chatbot API!"}


from .services.task_repository import TaskRepository
from .services.task_service import TaskService
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_async_session


# Dependency to get task service
async def get_task_service(db_session: AsyncSession = Depends(get_async_session)) -> TaskService:
    """
    Get an instance of TaskService with a repository using the provided database session.
    """
    task_repo = TaskRepository(db_session)
    task_service = TaskService(task_repo)
    return task_service


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "timestamp": "2026-02-05T10:00:00Z"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True  # Turn off in production
    )