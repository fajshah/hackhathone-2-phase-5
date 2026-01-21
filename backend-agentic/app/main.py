from fastapi import FastAPI
from app.api import app as api_app
from app.models import user, task, conversation  # Import models to register them
from app.db.session import engine
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

# Create all tables
SQLModel.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="Todo AI Chatbot Agentic Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Mount the API app
app.mount("/api/v1", api_app)

@app.get("/")
def read_root():
    return {"message": "Todo AI Chatbot Agentic Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}