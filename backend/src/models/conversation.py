"""
Conversation model for the Todo AI Chatbot.
Represents a thread of interaction between a user and the AI assistant.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User
    from .message import Message

# Define the Conversation model
class ConversationBase(SQLModel):
    """
    Base class for Conversation model with common fields.
    """
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a thread of interaction between a user and the AI assistant.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Foreign key to User
    user_id: int = Field(foreign_key="users.id", nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"

    def deactivate(self):
        """
        Mark the conversation as inactive.
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()


class ConversationCreate(ConversationBase):
    """
    Schema for creating a new conversation.
    """
    user_id: int  # Required when creating a conversation


class ConversationUpdate(SQLModel):
    """
    Schema for updating conversation information.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConversationPublic(ConversationBase):
    """
    Public representation of a conversation.
    """
    id: int
    uuid: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool