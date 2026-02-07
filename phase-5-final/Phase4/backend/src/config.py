"""
Configuration settings for the Todo AI Chatbot backend.
Manages environment variables and application settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_chatbot")

    # AI Provider settings
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai or openrouter
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo-preview")

    # Better Auth settings
    BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-here")
    BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:8000")

    # Application settings
    APP_NAME = "Todo AI Chatbot"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    VERSION = "1.0.0"

    # MCP Server settings
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))

# Create a settings instance
settings = Settings()