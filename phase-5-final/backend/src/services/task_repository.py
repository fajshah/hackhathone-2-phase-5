"""
Task repository service for CRUD operations on tasks.
Implements the data access layer for task management.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload
from ..models.task import Task, TaskStatus


class TaskRepository:
    """
    Repository class for Task entity operations
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task with the provided data.
        """
        task = Task(**task_data)
        # SQLAlchemy async session doesn't have add directly
        # We'll use the sync version for now
        self.db_session.add(task)
        await self.db_session.flush()  # This assigns the ID
        await self.db_session.refresh(task)
        return task

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by its ID.
        """
        result = await self.db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_tasks_by_user(self, user_id: str, status: Optional[TaskStatus] = None,
                                limit: int = 20, offset: int = 0) -> List[Task]:
        """
        Retrieve tasks for a specific user, optionally filtered by status.
        """
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)

        query = query.offset(offset).limit(limit)

        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task with the provided data.
        """
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .returning(Task)
        )
        result = await self.db_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        if updated_task:
            await self.db_session.refresh(updated_task)
            return updated_task

        return None

    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by its ID.
        """
        stmt = delete(Task).where(Task.id == task_id)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.rowcount > 0

    async def complete_task(self, task_id: str) -> Optional[Task]:
        """
        Mark a task as completed.
        """
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskStatus.COMPLETED, updated_at=datetime.utcnow())
            .returning(Task)
        )
        result = await self.db_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        if updated_task:
            await self.db_session.refresh(updated_task)
            return updated_task

        return None

    async def get_tasks_by_status(self, user_id: str, status: TaskStatus) -> List[Task]:
        """
        Get all tasks with a specific status for a user.
        """
        result = await self.db_session.execute(
            select(Task)
            .where(and_(Task.user_id == user_id, Task.status == status))
        )
        return result.scalars().all()

    async def assign_task(self, task_id: str, assigned_user_id: str) -> Optional[Task]:
        """
        Assign a task to a user.
        """
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(assigned_to=assigned_user_id, updated_at=datetime.utcnow())
            .returning(Task)
        )
        result = await self.db_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        if updated_task:
            await self.db_session.refresh(updated_task)
            return updated_task

        return None