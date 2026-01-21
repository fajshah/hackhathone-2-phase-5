"""
Main entry point for the Todo AI Chatbot backend application.
Sets up the FastAPI application with all necessary middleware and routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.error_handler import setup_error_handlers

# Import MCP tools to ensure they get registered with the server
from .mcp import mcp_server

# Import routers
from .api.chat import router as chat_router
from .api.auth import router as auth_router

# Create FastAPI app instance
app = FastAPI(
    title="Todo AI Chatbot API",
    version="1.0.0",
    description="AI-powered chatbot for managing todos through natural language"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Todo AI Chatbot API is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Todo AI Chatbot API"}

# Initialize database when app starts
from .database import init_db
@app.on_event("startup")
def startup_event():
    init_db()