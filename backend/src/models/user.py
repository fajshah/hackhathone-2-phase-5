"""
User model for the Todo AI Chatbot.
Represents a registered user of the application.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation
    from .message import Message

# Define user role enum
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

# Define the User model
class UserBase(SQLModel):
    """
    Base class for User model with common fields.
    """
    email: str = Field(unique=True, nullable=False, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class User(UserBase, table=True):
    """
    User model representing a registered user of the Todo AI Chatbot.
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Hashed password stored separately
    hashed_password: Optional[str] = Field(default=None, max_length=255)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
    conversations: List["Conversation"] = Relationship(back_populates="user", cascade_delete=True)
    messages: List["Message"] = Relationship(back_populates="user", cascade_delete=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

    def full_name(self) -> str:
        """
        Get the user's full name.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str
    email: str


class UserUpdate(SQLModel):
    """
    Schema for updating user information.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class UserPublic(UserBase):
    """
    Public representation of a user (without sensitive data).
    """
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime