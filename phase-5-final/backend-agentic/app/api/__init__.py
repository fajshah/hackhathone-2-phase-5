from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat_api import chat_endpoint, get_user_conversations, get_conversation_messages
from app.api.auth import router as auth_router

app = FastAPI(title="Todo AI Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.add_api_route("/users/{user_id}/chat/", chat_endpoint, methods=["POST"], tags=["chat"])
app.add_api_route("/users/{user_id}/conversations/", get_user_conversations, methods=["GET"], tags=["conversations"])
app.add_api_route("/conversations/{conversation_id}/messages/", get_conversation_messages, methods=["GET"], tags=["messages"])

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Todo AI Chatbot API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}