"""
Task API routes for the todo chatbot system.
Implements CRUD operations for tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..models.task import Task, TaskStatus, TaskPriority
from ..services.task_service import TaskService
from .models import TaskCreateRequest, TaskUpdateRequest, TaskResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session


# Dependency to get task service
async def get_task_service(db_session: AsyncSession = Depends(get_async_session)) -> TaskService:
    """
    Get an instance of TaskService with a repository using the provided database session.
    """
    from ..services.task_repository import TaskRepository
    task_repo = TaskRepository(db_session)
    task_service = TaskService(task_repo)
    return task_service


router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_request: TaskCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new task.
    """
    try:
        # Convert request model to dict
        task_data = task_request.dict()

        # Create the task
        task = await task_service.create_task(task_data)

        # Convert to response model
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            user_id=task.user_id,
            assigned_to=task.assigned_to,
            tags=task.tags
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str = Query(..., description="User ID to filter tasks"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get tasks for a user, with optional filtering.
    """
    try:
        tasks = await task_service.get_tasks_for_user(
            user_id=user_id,
            status=status.value if status else None,
            limit=limit,
            offset=offset
        )

        # Convert to response models
        return [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
                user_id=task.user_id,
                assigned_to=task.assigned_to,
                tags=task.tags
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Query(..., description="User ID"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get a specific task by ID.
    """
    try:
        task = await task_service.get_task_by_id(task_id, user_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or user not authorized"
            )

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            user_id=task.user_id,
            assigned_to=task.assigned_to,
            tags=task.tags
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdateRequest,
    user_id: str = Query(..., description="User ID"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Update a task.
    """
    try:
        # Convert update request to dict
        update_data = task_update.dict(exclude_unset=True)

        updated_task = await task_service.update_task(
            task_id=task_id,
            user_id=user_id,
            update_data=update_data
        )

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or user not authorized"
            )

        return TaskResponse(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            status=updated_task.status,
            priority=updated_task.priority,
            due_date=updated_task.due_date,
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at,
            user_id=updated_task.user_id,
            assigned_to=updated_task.assigned_to,
            tags=updated_task.tags
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user_id: str = Query(..., description="User ID"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Delete a task.
    """
    try:
        success = await task_service.delete_task(task_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or user not authorized"
            )

        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    user_id: str = Query(..., description="User ID"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Mark a task as completed.
    """
    try:
        completed_task = await task_service.complete_task(task_id, user_id)

        if not completed_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or user not authorized"
            )

        return TaskResponse(
            id=completed_task.id,
            title=completed_task.title,
            description=completed_task.description,
            status=completed_task.status,
            priority=completed_task.priority,
            due_date=completed_task.due_date,
            created_at=completed_task.created_at,
            updated_at=completed_task.updated_at,
            user_id=completed_task.user_id,
            assigned_to=completed_task.assigned_to,
            tags=completed_task.tags
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.post("/tasks/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: str,
    assigned_user_id: str = Query(..., description="User ID to assign the task to"),
    user_id: str = Query(..., description="User ID of the requester"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Assign a task to another user.
    """
    try:
        assigned_task = await task_service.assign_task(task_id, user_id, assigned_user_id)

        if not assigned_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or user not authorized"
            )

        return TaskResponse(
            id=assigned_task.id,
            title=assigned_task.title,
            description=assigned_task.description,
            status=assigned_task.status,
            priority=assigned_task.priority,
            due_date=assigned_task.due_date,
            created_at=assigned_task.created_at,
            updated_at=assigned_task.updated_at,
            user_id=assigned_task.user_id,
            assigned_to=assigned_task.assigned_to,
            tags=assigned_task.tags
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign task: {str(e)}"
        )