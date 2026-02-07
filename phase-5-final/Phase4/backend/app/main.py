from fastapi import FastAPI
from app.routers import auth, todos, conversations
from app.database import engine
from app.models import user, todo, conversation  # Import models to create tables
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create tables
user.SQLModel.metadata.create_all(bind=engine)
todo.SQLModel.metadata.create_all(bind=engine)
conversation.SQLModel.metadata.create_all(bind=engine)

app = FastAPI(title="Todo AI Chatbot API", version="1.0.0")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])

@app.get("/")
def read_root():
    return {"message": "Todo AI Chatbot API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}