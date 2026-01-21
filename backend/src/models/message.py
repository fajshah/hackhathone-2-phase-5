"""
Message model for the Todo AI Chatbot.
Represents an individual exchange in a conversation.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation

# Define message role enum
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Define the Message model
class MessageBase(SQLModel):
    """
    Base class for Message model with common fields.
    """
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)  # Allow longer messages
    sequence_number: Optional[int] = Field(default=None)  # Order of messages in conversation


class Message(MessageBase, table=True):
    """
    Message model representing an individual exchange in a conversation.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    user_id: int = Field(foreign_key="users.id", nullable=False)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"

    def update_content(self, new_content: str):
        """
        Update the message content and update the timestamp.
        """
        self.content = new_content
        self.updated_at = datetime.utcnow()


class MessageCreate(MessageBase):
    """
    Schema for creating a new message.
    """
    user_id: int
    conversation_id: int
    content: str


class MessageUpdate(SQLModel):
    """
    Schema for updating message information.
    """
    content: Optional[str] = None
    sequence_number: Optional[int] = None


class MessagePublic(MessageBase):
    """
    Public representation of a message.
    """
    id: int
    uuid: str
    user_id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime