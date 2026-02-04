from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    due_date: Optional[datetime] = None
    category: Optional[str] = None

class Todo(TodoBase, table=True):
    __tablename__ = "todos"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    due_date: Optional[datetime] = None
    category: Optional[str] = None
    owner_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())
    completed_at: Optional[datetime] = None

    # Relationship
    owner: "User" = Relationship(back_populates="todos")

class TodoCreate(TodoBase):
    pass

class TodoRead(TodoBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    due_date: Optional[datetime] = None
    category: Optional[str] = None