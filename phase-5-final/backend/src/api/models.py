"""
API request/response models for the todo chatbot system.
Defines Pydantic models for all API endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from ..models.task import TaskStatus, TaskPriority


class TaskCreateRequest(BaseModel):
    """
    Request model for creating a new task
    """
    title: str = Field(..., min_length=1, max_length=255, description="Task title or description")
    description: Optional[str] = Field(None, description="Optional detailed description")
    status: Optional[TaskStatus] = Field(default=TaskStatus.PENDING, description="Initial status of the task")
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM, description="Priority level of the task")
    due_date: Optional[datetime] = Field(None, description="Optional deadline for task completion")
    user_id: str = Field(..., description="ID of the user who owns the task")
    assigned_to: Optional[str] = Field(None, description="Optional user ID to assign task to")
    tags: List[str] = Field(default=[], description="Array of tags for categorization")


class TaskUpdateRequest(BaseModel):
    """
    Request model for updating an existing task
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, description="Updated detailed description")
    status: Optional[TaskStatus] = Field(None, description="Updated status of the task")
    priority: Optional[TaskPriority] = Field(None, description="Updated priority level")
    due_date: Optional[datetime] = Field(None, description="Updated deadline for task completion")
    assigned_to: Optional[str] = Field(None, description="Updated user assignment")


class TaskResponse(BaseModel):
    """
    Response model for task operations
    """
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: str
    assigned_to: Optional[str] = None
    tags: List[str] = []


class ChatMessageRequest(BaseModel):
    """
    Request model for chat messages
    """
    message: str = Field(..., description="User's message to the chatbot")
    user_id: str = Field(..., description="ID of the user sending the message")
    context: Optional[str] = Field(None, description="Conversation context identifier")


class ChatMessageResponse(BaseModel):
    """
    Response model for chat messages
    """
    response: str = Field(..., description="Chatbot's natural language response")
    actions: List[dict] = Field(default=[], description="List of actions performed")
    context: Optional[str] = Field(None, description="Updated conversation context")


class ReminderCreateRequest(BaseModel):
    """
    Request model for creating a reminder
    """
    task_id: str = Field(..., description="ID of the task to remind about")
    user_id: str = Field(..., description="ID of the user receiving the reminder")
    scheduled_time: datetime = Field(..., description="When to send the reminder")
    method: str = Field(default="in-app", description="Method of delivery for the reminder")


class ReminderResponse(BaseModel):
    """
    Response model for reminder operations
    """
    id: str
    task_id: str
    user_id: str
    scheduled_time: datetime
    status: str
    method: str
    created_at: datetime
    sent_at: Optional[datetime] = None