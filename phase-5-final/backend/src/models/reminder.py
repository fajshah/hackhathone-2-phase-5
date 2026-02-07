import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from enum import Enum


class ReminderStatus(str, Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    CANCELLED = "cancelled"


class ReminderMethod(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in-app"


class Reminder(SQLModel, table=True):
    """
    Represents scheduled notifications for tasks
    """
    __tablename__ = "reminders"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="Unique identifier for the reminder")
    task_id: str = Field(description="Reference to associated task")
    user_id: str = Field(description="Reference to user receiving reminder")
    scheduled_time: datetime = Field(sa_column=Column(DateTime, nullable=False), description="When reminder should be sent")
    status: ReminderStatus = Field(default=ReminderStatus.SCHEDULED, description="Current status of the reminder")
    method: ReminderMethod = Field(default=ReminderMethod.IN_APP, description="Method of delivery for the reminder")
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="Timestamp of creation")
    sent_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="Timestamp when reminder was sent (nullable)")