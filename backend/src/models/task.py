"""
Task model for the Todo AI Chatbot.
Represents a todo item that belongs to a user.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from .user import User

# Define task priority enum
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Define task status enum
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Define the Task model
class TaskBase(SQLModel):
    """
    Base class for Task model with common fields.
    """
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """
    Task model representing a todo item that belongs to a user.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Foreign key to User
    user_id: int = Field(foreign_key="users.id", nullable=False)

    # Relationship
    user: "User" = Relationship(back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', user_id={self.user_id})>"

    def mark_completed(self):
        """
        Mark the task as completed and set the completed_at timestamp.
        """
        self.completed = True
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    title: str
    user_id: int  # Required when creating a task


class TaskUpdate(SQLModel):
    """
    Schema for updating task information.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskPublic(TaskBase):
    """
    Public representation of a task.
    """
    id: int
    uuid: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]