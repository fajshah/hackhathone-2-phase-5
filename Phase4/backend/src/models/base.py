"""
Base model for all SQLModel entities in the Todo AI Chatbot.
Provides common fields and functionality for all database models.
"""
from sqlmodel import SQLModel as _SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class SQLModel(_SQLModel):
    """
    Extended SQLModel base class that provides common functionality
    for all models in the Todo AI Chatbot application.
    """
    class Config:
        arbitrary_types_allowed = True

def generate_uuid():
    """
    Generate a UUID4 string for use as a default value in models.
    """
    return str(uuid.uuid4())

class TimestampMixin:
    """
    Mixin class that adds created_at and updated_at timestamp fields
    to models that inherit from it.
    """
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class BaseModel(SQLModel, TimestampMixin, table=False):
    """
    Base model that combines SQLModel with TimestampMixin.
    All models in the Todo AI Chatbot application should inherit from this.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=generate_uuid, unique=True, nullable=False)