import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class UserSession(SQLModel, table=True):
    """
    Maintains conversational state for user interactions
    """
    __tablename__ = "user_sessions"

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="Unique session identifier")
    user_id: str = Field(description="Reference to user")
    current_context: str = Field(default="", description="Current conversational context")
    last_interaction: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="Timestamp of last chat interaction")
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="Session creation time")
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24), sa_column=Column(DateTime, nullable=False), description="Session expiration time")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Current status of the session")