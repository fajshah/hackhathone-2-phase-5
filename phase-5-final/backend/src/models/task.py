import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, String, JSON
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    IN_PROGRESS = "in-progress"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(SQLModel, table=True):
    """
    Represents a user's to-do item with associated metadata and status
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="Unique identifier for the task")
    title: str = Field(min_length=1, max_length=255, description="Task title/description")
    description: Optional[str] = Field(None, description="Optional detailed description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priority level of the task")
    due_date: Optional[datetime] = Field(None, sa_column=Column(DateTime, nullable=True), description="Optional deadline for task completion")
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="Timestamp of last update")
    user_id: str = Field(description="Reference to user who owns the task")
    assigned_to: Optional[str] = Field(None, description="Reference to user assigned to task (optional)")
    tags: List[str] = Field(default=[], sa_column=Column(JSON, nullable=False), description="Array of string tags for categorization")