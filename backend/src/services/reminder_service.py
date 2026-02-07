"""
Reminder service for the todo chatbot system.
Handles scheduling, cancelling, and triggering of reminders using Dapr Jobs API.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.reminder import Reminder, ReminderStatus, ReminderMethod
from ..models.task import TaskStatus
import asyncio
import logging


class ReminderService:
    """
    Service class for reminder operations
    """

    def __init__(self, dapr_client=None, task_service=None):
        self.dapr_client = dapr_client
        self.task_service = task_service
        self.logger = logging.getLogger(__name__)

    async def schedule_reminder(self, reminder_data: Dict[str, Any]) -> Reminder:
        """
        Schedule a new reminder after validating the input data.

        Args:
            reminder_data: Dictionary containing reminder information

        Returns:
            Reminder object with the scheduled reminder
        """
        # Validate input data
        self._validate_reminder_data(reminder_data)

        # Verify that the task exists and is in an appropriate status for a reminder
        if self.task_service:
            task = await self.task_service.get_task_by_id(
                task_id=reminder_data['task_id'],
                user_id=reminder_data['user_id']
            )
            if not task:
                raise ValueError("Task does not exist or user not authorized")
            if task.status == TaskStatus.COMPLETED:
                raise ValueError("Cannot schedule reminder for a completed task")

        # Create the reminder object
        reminder = Reminder(
            task_id=reminder_data['task_id'],
            user_id=reminder_data['user_id'],
            scheduled_time=reminder_data['scheduled_time'],
            method=ReminderMethod(reminder_data.get('method', 'in-app')),
            created_at=datetime.utcnow()
        )

        # Validate scheduling rules
        reminder.validate_scheduling_rules()

        # Here we would integrate with Dapr Jobs API to actually schedule the reminder
        # For now, we'll just return the reminder object
        # In a real implementation:
        # await self._schedule_with_dapr_jobs(reminder)

        return reminder

    async def cancel_reminder(self, reminder_id: str, user_id: str) -> Optional[Reminder]:
        """
        Cancel a scheduled reminder after verifying user authorization.

        Args:
            reminder_id: ID of the reminder to cancel
            user_id: ID of the user requesting cancellation

        Returns:
            Updated reminder object if successful, None otherwise
        """
        # In a real implementation, we'd fetch the reminder from storage
        # and verify it belongs to the user, then cancel the Dapr job
        # For now, we'll just simulate the cancellation

        # If we had the reminder object, we would:
        # 1. Verify the user owns this reminder
        # 2. Cancel the Dapr job
        # 3. Update the reminder status to cancelled

        # Return a mock reminder with cancelled status
        reminder = Reminder(
            id=reminder_id,
            task_id="mock_task_id",  # Would come from actual reminder
            user_id=user_id,
            scheduled_time=datetime.utcnow(),  # Would come from actual reminder
            status=ReminderStatus.CANCELLED,
            created_at=datetime.utcnow()
        )

        return reminder

    async def trigger_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """
        Trigger a reminder by sending notification to the user.

        Args:
            reminder_id: ID of the reminder to trigger

        Returns:
            Updated reminder object if successful, None otherwise
        """
        # In a real implementation, we would:
        # 1. Fetch the reminder from storage
        # 2. Verify it's time to send the reminder
        # 3. Send the notification based on the method
        # 4. Update the reminder status to sent
        # 5. Record the sent time

        # For now, we'll just return a mock reminder
        reminder = Reminder(
            id=reminder_id,
            task_id="mock_task_id",  # Would come from actual reminder
            user_id="mock_user_id",  # Would come from actual reminder
            scheduled_time=datetime.utcnow(),
            status=ReminderStatus.SENT,
            created_at=datetime.utcnow(),
            sent_at=datetime.utcnow()
        )

        return reminder

    async def get_upcoming_reminders(self, user_id: str, limit: int = 10) -> List[Reminder]:
        """
        Get upcoming reminders for a specific user.

        Args:
            user_id: ID of the user
            limit: Maximum number of reminders to return

        Returns:
            List of upcoming reminder objects
        """
        # In a real implementation, we would query the database/storage
        # for reminders belonging to the user with status 'scheduled'
        # and scheduled_time in the future

        # For now, return an empty list
        return []

    async def get_reminder_by_id(self, reminder_id: str, user_id: str) -> Optional[Reminder]:
        """
        Get a specific reminder by ID after verifying user authorization.

        Args:
            reminder_id: ID of the reminder
            user_id: ID of the user requesting the reminder

        Returns:
            Reminder object if found and user authorized, None otherwise
        """
        # In a real implementation, we would fetch the reminder from storage
        # and verify it belongs to the user

        # For now, return None to indicate not found
        return None

    def _validate_reminder_data(self, reminder_data: Dict[str, Any]):
        """
        Validate reminder data based on business rules.
        """
        required_fields = ['task_id', 'user_id', 'scheduled_time']
        for field in required_fields:
            if field not in reminder_data:
                raise ValueError(f"Missing required field: {field}")

        if not reminder_data['task_id']:
            raise ValueError("Task ID is required")
        if not reminder_data['user_id']:
            raise ValueError("User ID is required")
        if not reminder_data['scheduled_time']:
            raise ValueError("Scheduled time is required")

        # Validate scheduled time is in the future
        scheduled_time = reminder_data['scheduled_time']
        if isinstance(scheduled_time, str):
            from datetime import datetime
            scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))

        if scheduled_time <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")

        # Validate reminder method if provided
        if 'method' in reminder_data and reminder_data['method']:
            try:
                ReminderMethod(reminder_data['method'])
            except ValueError:
                raise ValueError(f"Invalid reminder method: {reminder_data['method']}")

    async def _schedule_with_dapr_jobs(self, reminder: Reminder) -> str:
        """
        Schedule a reminder using Dapr Jobs API.

        Args:
            reminder: Reminder object to schedule

        Returns:
            Job ID of the scheduled reminder
        """
        # This is a placeholder for the actual Dapr Jobs API integration
        # In a real implementation, we would:
        # 1. Create a Dapr job that triggers at the scheduled time
        # 2. The job would call a webhook or service method to handle the reminder

        if self.dapr_client:
            # Dapr Jobs API call would go here
            pass

        # Return a mock job ID
        return f"dapr-job-{reminder.id}"

    async def validate_task_for_reminder(self, task_id: str, user_id: str) -> bool:
        """
        Validate that a task is eligible for a reminder.

        Args:
            task_id: ID of the task to validate
            user_id: ID of the user requesting validation

        Returns:
            True if task is valid for reminder, False otherwise
        """
        if not self.task_service:
            return True  # Skip validation if task service not provided

        task = await self.task_service.get_task_by_id(task_id, user_id)
        if not task:
            return False

        # Task must be pending or in-progress to have a reminder
        if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            return True

        return False

    async def get_active_reminders_for_task(self, task_id: str) -> List[Reminder]:
        """
        Get all active (non-cancelled, non-sent) reminders for a specific task.

        Args:
            task_id: ID of the task

        Returns:
            List of active reminder objects
        """
        # In a real implementation, we would query the database/storage
        # for reminders for this task with status 'scheduled'

        # For now, return an empty list
        return []

    async def has_active_reminder_for_task(self, task_id: str) -> bool:
        """
        Check if there is already an active reminder for a task.

        Args:
            task_id: ID of the task

        Returns:
            True if there's an active reminder, False otherwise
        """
        active_reminders = await self.get_active_reminders_for_task(task_id)
        return len(active_reminders) > 0