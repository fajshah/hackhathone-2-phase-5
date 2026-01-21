"""
Task service for the Todo AI Chatbot.
Handles CRUD operations for Task model with proper user authorization.
"""
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from ..models.user import User
from datetime import datetime


class TaskService:
    """
    Service class for handling task-related operations.
    Implements CRUD operations with proper user authorization.
    """

    @staticmethod
    def create_task(session: Session, task_create: TaskCreate, user: User) -> Task:
        """
        Create a new task for the authenticated user.
        Verifies that the task is being created for the correct user.
        """
        # Verify that the user_id in the request matches the authenticated user
        if task_create.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create task for this user"
            )

        # Create the task instance
        task = Task.from_orm(task_create) if hasattr(Task, 'from_orm') else Task(**task_create.dict())
        task.user_id = user.id

        # Add to session and commit
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def get_task_by_id(session: Session, task_id: int, user: User) -> Optional[Task]:
        """
        Retrieve a task by its ID for the authenticated user.
        Returns None if the task doesn't exist or doesn't belong to the user.
        """
        # Query for the task belonging to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
        task = session.exec(statement).first()
        return task

    @staticmethod
    def get_tasks_by_user(
        session: Session,
        user: User,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        Retrieve all tasks for the authenticated user with optional filtering.
        """
        # Start with a base query for tasks belonging to the user
        statement = select(Task).where(Task.user_id == user.id)

        # Apply filters if provided
        if status:
            statement = statement.where(Task.status == status)
        if priority:
            statement = statement.where(Task.priority == priority)

        # Apply pagination
        statement = statement.offset(offset).limit(limit)

        # Execute query
        tasks = session.exec(statement).all()
        return tasks

    @staticmethod
    def update_task(session: Session, task_id: int, task_update: TaskUpdate, user: User) -> Optional[Task]:
        """
        Update a task for the authenticated user.
        Returns the updated task or None if the task doesn't exist or doesn't belong to the user.
        """
        # Get the existing task
        task = TaskService.get_task_by_id(session, task_id, user)
        if not task:
            return None

        # Update the task with the provided fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update the timestamp
        task.updated_at = datetime.utcnow()

        # Commit changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user: User) -> bool:
        """
        Delete a task for the authenticated user.
        Returns True if the task was deleted, False if it didn't exist or didn't belong to the user.
        """
        # Get the task to delete
        task = TaskService.get_task_by_id(session, task_id, user)
        if not task:
            return False

        # Delete the task
        session.delete(task)
        session.commit()

        return True

    @staticmethod
    def mark_task_completed(session: Session, task_id: int, user: User) -> Optional[Task]:
        """
        Mark a task as completed for the authenticated user.
        Returns the updated task or None if the task doesn't exist or doesn't belong to the user.
        """
        # Get the task to update
        task = TaskService.get_task_by_id(session, task_id, user)
        if not task:
            return None

        # Mark as completed
        task.mark_completed()

        # Commit changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def get_pending_tasks_count(session: Session, user: User) -> int:
        """
        Get the count of pending tasks for the authenticated user.
        """
        statement = select(Task).where(
            Task.user_id == user.id,
            Task.status == TaskStatus.PENDING
        )
        tasks = session.exec(statement).all()
        return len(tasks)


# Create a singleton instance of the service
task_service = TaskService()