"""
Task service for business logic related to task management.
Handles validation, business rules, and orchestrates task operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.task import Task, TaskStatus, TaskPriority
from .task_repository import TaskRepository


class TaskService:
    """
    Service class for Task business operations
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task after validating the input data.
        """
        # Validate input data
        await self._validate_task_data(task_data)

        # Set default values if not provided
        if 'status' not in task_data or task_data['status'] is None:
            task_data['status'] = TaskStatus.PENDING.value
        if 'priority' not in task_data or task_data['priority'] is None:
            task_data['priority'] = TaskPriority.MEDIUM.value
        if 'created_at' not in task_data or task_data['created_at'] is None:
            task_data['created_at'] = datetime.utcnow()
        if 'updated_at' not in task_data or task_data['updated_at'] is None:
            task_data['updated_at'] = datetime.utcnow()

        # Validate due date if provided
        if 'due_date' in task_data and task_data['due_date']:
            if isinstance(task_data['due_date'], str):
                from datetime import datetime
                task_data['due_date'] = datetime.fromisoformat(task_data['due_date'])
            if task_data['due_date'] < datetime.utcnow() and task_data['status'] == TaskStatus.PENDING.value:
                raise ValueError("Due date cannot be in the past when status is pending")

        # Create the task
        return await self.task_repository.create_task(task_data)

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Retrieve a task by its ID, ensuring it belongs to the specified user.
        """
        task = await self.task_repository.get_task_by_id(task_id)
        if task and task.user_id == user_id:
            return task
        return None

    async def get_tasks_for_user(self, user_id: str, status: Optional[str] = None,
                                 limit: int = 20, offset: int = 0) -> List[Task]:
        """
        Retrieve tasks for a specific user, optionally filtered by status.
        """
        task_status = TaskStatus(status) if status else None
        return await self.task_repository.get_tasks_by_user(user_id, task_status, limit, offset)

    async def update_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task after validating the user has permission and the data is valid.
        """
        # Get the existing task to verify user ownership
        existing_task = await self.task_repository.get_task_by_id(task_id)
        if not existing_task or existing_task.user_id != user_id:
            return None

        # Validate update data
        await self._validate_task_data(update_data, for_update=True)

        # Update timestamps
        update_data['updated_at'] = datetime.utcnow()

        # Validate due date if being updated
        if 'due_date' in update_data and update_data['due_date']:
            if isinstance(update_data['due_date'], str):
                from datetime import datetime
                update_data['due_date'] = datetime.fromisoformat(update_data['due_date'])
            if update_data['due_date'] < datetime.utcnow() and existing_task.status == TaskStatus.PENDING:
                raise ValueError("Due date cannot be in the past when status is pending")

        # Perform the update
        return await self.task_repository.update_task(task_id, update_data)

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task after verifying user ownership.
        """
        # Verify user ownership
        task = await self.task_repository.get_task_by_id(task_id)
        if not task or task.user_id != user_id:
            return False

        return await self.task_repository.delete_task(task_id)

    async def complete_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Mark a task as completed after verifying user ownership.
        """
        # Verify user ownership
        task = await self.task_repository.get_task_by_id(task_id)
        if not task or task.user_id != user_id:
            return None

        # Update the task status to completed
        return await self.task_repository.complete_task(task_id)

    async def assign_task(self, task_id: str, user_id: str, assigned_user_id: str) -> Optional[Task]:
        """
        Assign a task to another user after verifying original user ownership.
        """
        # Verify user ownership
        task = await self.task_repository.get_task_by_id(task_id)
        if not task or task.user_id != user_id:
            return None

        # Perform the assignment
        return await self.task_repository.assign_task(task_id, assigned_user_id)

    async def _validate_task_data(self, task_data: Dict[str, Any], for_update: bool = False) -> None:
        """
        Validate task data based on business rules.
        """
        if not for_update or 'title' in task_data:
            if 'title' not in task_data or not task_data['title'] or len(task_data['title']) > 255:
                raise ValueError("Title is required and must be 1-255 characters long")

        if 'status' in task_data and task_data['status']:
            try:
                TaskStatus(task_data['status'])
            except ValueError:
                raise ValueError(f"Invalid status: {task_data['status']}")

        if 'priority' in task_data and task_data['priority']:
            try:
                TaskPriority(task_data['priority'])
            except ValueError:
                raise ValueError(f"Invalid priority: {task_data['priority']}")

        if 'due_date' in task_data and task_data['due_date']:
            # Already validated when parsing date in create/update methods
            pass

        if 'user_id' in task_data and not task_data['user_id']:
            raise ValueError("user_id is required")

    def _validate_task_transition(self, current_status: TaskStatus, new_status: TaskStatus) -> bool:
        """
        Validate state transitions based on business rules:
        - pending → in-progress → completed
        - completed → pending (only through explicit user action)
        - pending → cancelled (through explicit user action)
        """
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.PENDING],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS],
            TaskStatus.COMPLETED: [TaskStatus.PENDING, TaskStatus.COMPLETED],
        }

        return new_status in valid_transitions.get(current_status, [current_status])

    async def update_task_status(self, task_id: str, user_id: str, new_status: str) -> Optional[Task]:
        """
        Update task status with transition validation.
        """
        task = await self.task_repository.get_task_by_id(task_id)
        if not task or task.user_id != user_id:
            return None

        # Validate status transition
        new_status_enum = TaskStatus(new_status)
        if not self._validate_task_transition(task.status, new_status_enum):
            raise ValueError(f"Invalid status transition: {task.status.value} -> {new_status}")

        # Update status
        update_data = {
            'status': new_status_enum.value,
            'updated_at': datetime.utcnow()
        }

        return await self.task_repository.update_task(task_id, update_data)