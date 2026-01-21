from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import JSON

class MessageBase(SQLModel):
    role: str  # "user" or "assistant"
    content: str

class Message(MessageBase, table=True):
    __tablename__ = "messages"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role: str  # "user" or "assistant"
    content: str
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())

class ConversationBase(SQLModel):
    title: str

class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())
    is_active: bool = True

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class ConversationCreate(ConversationBase):
    pass

class ConversationRead(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

class ConversationUpdate(SQLModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None