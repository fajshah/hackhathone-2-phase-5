"""
Event Log model for the todo chatbot system.
Represents logged events for audit trail and replay capability.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, JSON
from enum import Enum
import uuid


class EventType(str, Enum):
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    TASK_ASSIGNED = "task.assigned"

    # Reminder events
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_CANCELLED = "reminder.cancelled"
    REMINDER_TRIGGERED = "reminder.triggered"
    REMINDER_SENT = "reminder.sent"

    # System events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    HEALTH_CHECK = "system.health.check"
    API_CALL = "api.call"


class EventLog(SQLModel, table=True):
    """
    Represents a logged event for audit trail and replay capability
    """
    __tablename__ = "event_logs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="Unique event identifier")
    event_type: EventType = Field(description="Type of event (task-created, reminder-scheduled, etc.)")
    payload: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False), description="Event data in JSON format")
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False), description="When event occurred")
    source_service: str = Field(description="Which service generated the event")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="For tracking related events")
    user_id: Optional[str] = Field(default=None, description="User associated with the event (if applicable)")
    task_id: Optional[str] = Field(default=None, description="Task associated with the event (if applicable)")
    event_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON), description="Additional metadata about the event")

    def __init__(self, **data):
        super().__init__(**data)

        # Set default values for certain fields if not provided
        if 'source_service' not in data:
            self.source_service = "todo-chatbot-backend"
        if 'metadata' not in data:
            self.metadata = {}

        # Ensure payload is always a dict
        if 'payload' not in data or self.payload is None:
            self.payload = {}

    @classmethod
    def create_task_event(cls, event_type: EventType, task_data: Dict[str, Any],
                         user_id: str = None, correlation_id: str = None) -> 'EventLog':
        """
        Factory method to create a task-related event log entry.

        Args:
            event_type: The type of task event
            task_data: The task data to include in the event
            user_id: The user associated with the event
            correlation_id: Optional correlation ID

        Returns:
            EventLog instance
        """
        event_data = {
            "event_type": event_type,
            "payload": {
                "task": task_data
            },
            "source_service": "todo-chatbot-backend",
            "user_id": user_id,
            "task_id": task_data.get("id") if task_data else None
        }

        if correlation_id:
            event_data["correlation_id"] = correlation_id

        return cls(**event_data)

    @classmethod
    def create_reminder_event(cls, event_type: EventType, reminder_data: Dict[str, Any],
                            user_id: str = None, correlation_id: str = None) -> 'EventLog':
        """
        Factory method to create a reminder-related event log entry.

        Args:
            event_type: The type of reminder event
            reminder_data: The reminder data to include in the event
            user_id: The user associated with the event
            correlation_id: Optional correlation ID

        Returns:
            EventLog instance
        """
        event_data = {
            "event_type": event_type,
            "payload": {
                "reminder": reminder_data
            },
            "source_service": "todo-chatbot-backend",
            "user_id": user_id,
            "task_id": reminder_data.get("task_id") if reminder_data else None
        }

        if correlation_id:
            event_data["correlation_id"] = correlation_id

        return cls(**event_data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event log to a dictionary representation.

        Returns:
            Dictionary representation of the event log
        """
        return {
            "id": self.id,
            "event_type": self.event_type.value if hasattr(self.event_type, 'value') else self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source_service": self.source_service,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "metadata": self.metadata
        }

    def is_audit_trail_eligible(self) -> bool:
        """
        Check if this event should be included in audit trails.

        Returns:
            True if the event is eligible for audit trail, False otherwise
        """
        # In general, all events are audit trail eligible
        # But we might exclude health checks and other routine events
        return self.event_type not in [EventType.HEALTH_CHECK]

    def get_related_entities(self) -> Dict[str, str]:
        """
        Get entity IDs related to this event.

        Returns:
            Dictionary of entity type to ID
        """
        entities = {}
        if self.user_id:
            entities["user"] = self.user_id
        if self.task_id:
            entities["task"] = self.task_id
        return entities

    def matches_criteria(self, event_types: Optional[list] = None,
                       user_id: Optional[str] = None,
                       task_id: Optional[str] = None,
                       date_range: Optional[tuple] = None) -> bool:
        """
        Check if this event matches specified criteria.

        Args:
            event_types: List of event types to match
            user_id: Specific user ID to match
            task_id: Specific task ID to match
            date_range: Tuple of (start_date, end_date) to match

        Returns:
            True if the event matches the criteria, False otherwise
        """
        # Check event type
        if event_types and self.event_type not in event_types:
            return False

        # Check user ID
        if user_id and self.user_id != user_id:
            return False

        # Check task ID
        if task_id and self.task_id != task_id:
            return False

        # Check date range
        if date_range:
            start_date, end_date = date_range
            if start_date and self.timestamp < start_date:
                return False
            if end_date and self.timestamp > end_date:
                return False

        return True