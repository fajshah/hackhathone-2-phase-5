"""
MCP tools for task operations in the Todo AI Chatbot.
Contains tools for adding, listing, updating, and managing tasks.
"""
from typing import Dict, Any
from sqlmodel import Session
from ...models.task import Task, TaskCreate
from ...models.user import User
from ...services.task_service import task_service
from ..server import mcp_server
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_task(session: Session, user: User, title: str, description: str = None) -> Dict[str, Any]:
    """
    MCP Tool: Add a new task for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        title: Task title
        description: Optional task description

    Returns:
        Dictionary with task information
    """
    logger.info(f"MCP tool 'add_task' called for user {user.id} with title '{title}'")

    # Prepare the task creation data
    task_create = TaskCreate(
        title=title,
        description=description,
        user_id=user.id
    )

    # Create the task using the service
    task = task_service.create_task(session, task_create, user)

    logger.info(f"Task created successfully with ID {task.id}")

    # Return the created task information
    return {
        "task_id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "status": task.status.value,
        "priority": task.priority.value
    }


def list_tasks(session: Session, user: User, status: str = "all", priority: str = None, sort_by: str = "created_at", order: str = "asc", due_date_start: str = None, due_date_end: str = None) -> Dict[str, Any]:
    """
    MCP Tool: List tasks for the authenticated user with filtering and sorting options.

    Args:
        session: Database session
        user: Authenticated user
        status: Task status filter (all, pending, completed, in_progress, cancelled)
        priority: Task priority filter (low, medium, high, urgent)
        sort_by: Field to sort by (created_at, due_date, priority, status)
        order: Sort order (asc, desc)
        due_date_start: Filter tasks with due date on or after this date (ISO format)
        due_date_end: Filter tasks with due date on or before this date (ISO format)

    Returns:
        Dictionary with list of tasks
    """
    logger.info(f"MCP tool 'list_tasks' called for user {user.id} with filters - status: {status}, priority: {priority}, sort_by: {sort_by}, order: {order}")

    # Map string status to enum
    from ..models.task import TaskStatus, TaskPriority
    status_enum = None
    if status.lower() != "all":
        try:
            status_enum = TaskStatus(status.lower())
        except ValueError:
            logger.warning(f"Invalid status filter '{status}', defaulting to 'all'")

    # Map string priority to enum
    priority_enum = None
    if priority:
        try:
            priority_enum = TaskPriority(priority.lower())
        except ValueError:
            logger.warning(f"Invalid priority filter '{priority}', ignoring")

    # Get tasks using the service
    tasks = task_service.get_tasks_by_user(session, user, status=status_enum, priority=priority_enum)

    # Apply date range filtering if specified
    from datetime import datetime
    filtered_tasks = tasks
    if due_date_start:
        try:
            start_date = datetime.fromisoformat(due_date_start.replace('Z', '+00:00'))
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date >= start_date]
        except ValueError:
            logger.warning(f"Invalid due_date_start format: {due_date_start}, ignoring")

    if due_date_end:
        try:
            end_date = datetime.fromisoformat(due_date_end.replace('Z', '+00:00'))
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date <= end_date]
        except ValueError:
            logger.warning(f"Invalid due_date_end format: {due_date_end}, ignoring")

    # Apply sorting
    reverse_order = order.lower() == "desc"
    if sort_by == "due_date":
        filtered_tasks.sort(key=lambda t: t.due_date or datetime.min, reverse=reverse_order)
    elif sort_by == "priority":
        # Sort by priority level (urgency)
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        filtered_tasks.sort(key=lambda t: priority_order.get(t.priority.value, 4), reverse=reverse_order)
    elif sort_by == "status":
        # Sort by status (completed, in_progress, pending, cancelled)
        status_order = {"completed": 0, "in_progress": 1, "pending": 2, "cancelled": 3}
        filtered_tasks.sort(key=lambda t: status_order.get(t.status.value, 4), reverse=reverse_order)
    else:  # Default to created_at
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=reverse_order)

    logger.info(f"Found {len(filtered_tasks)} tasks for user {user.id} after filtering")

    # Format tasks for return
    tasks_list = []
    for task in filtered_tasks:
        tasks_list.append({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status.value,
            "priority": task.priority.value
        })

    return {
        "tasks": tasks_list,
        "total_count": len(tasks_list),
        "status_filter": status,
        "priority_filter": priority,
        "sort_by": sort_by,
        "order": order,
        "date_range": {
            "start": due_date_start,
            "end": due_date_end
        }
    }


def complete_task(session: Session, user: User, task_id: int, confirm: bool = False) -> Dict[str, Any]:
    """
    MCP Tool: Mark a task as completed for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        task_id: ID of the task to complete
        confirm: Whether to require confirmation before completion

    Returns:
        Dictionary with updated task information
    """
    logger.info(f"MCP tool 'complete_task' called for user {user.id} and task {task_id}, confirm: {confirm}")

    # First, get the task to check if it exists and belongs to the user
    task = task_service.get_task_by_id(session, task_id, user)

    if not task:
        logger.error(f"Task {task_id} not found for user {user.id}")
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found or not owned by user",
            "task_id": task_id
        }

    # If confirmation is required and not provided, return a confirmation request
    if confirm and not _check_confirmation_needed(session, user, task_id, "complete"):
        return {
            "success": False,
            "needs_confirmation": True,
            "message": f"Task '{task.title}' will be marked as completed. Please confirm completion.",
            "task_id": task_id,
            "task_title": task.title
        }

    # Update the task using the service
    task = task_service.mark_task_completed(session, task_id, user)

    if not task:
        logger.error(f"Task {task_id} not found for user {user.id}")
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found or not owned by user",
            "task_id": task_id
        }

    logger.info(f"Task {task_id} marked as completed successfully")

    # Return the updated task information
    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "completed": task.completed,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "status": task.status.value
    }


def delete_task(session: Session, user: User, task_id: int, confirm: bool = False) -> Dict[str, Any]:
    """
    MCP Tool: Delete a task for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        task_id: ID of the task to delete
        confirm: Whether to require confirmation before deletion

    Returns:
        Dictionary with deletion result
    """
    logger.info(f"MCP tool 'delete_task' called for user {user.id} and task {task_id}, confirm: {confirm}")

    # First, get the task to check if it exists and belongs to the user
    task = task_service.get_task_by_id(session, task_id, user)

    if not task:
        logger.error(f"Task {task_id} not found for user {user.id}")
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found or not owned by user",
            "task_id": task_id
        }

    # If confirmation is required and not provided, return a confirmation request
    if confirm and not _check_confirmation_needed(session, user, task_id, "delete"):
        return {
            "success": False,
            "needs_confirmation": True,
            "message": f"Task '{task.title}' will be permanently deleted. Please confirm deletion.",
            "task_id": task_id,
            "task_title": task.title
        }

    # Delete the task using the service
    success = task_service.delete_task(session, task_id, user)

    if not success:
        logger.error(f"Failed to delete task {task_id} for user {user.id}")
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found or not owned by user",
            "task_id": task_id
        }

    logger.info(f"Task {task_id} deleted successfully")

    return {
        "success": True,
        "task_id": task_id,
        "message": f"Task '{task.title}' has been deleted successfully"
    }


def _check_confirmation_needed(session: Session, user: User, task_id: int, action: str) -> bool:
    """
    Internal function to check if confirmation is needed for sensitive operations.

    Args:
        session: Database session
        user: Authenticated user
        task_id: ID of the task
        action: The action being performed

    Returns:
        Boolean indicating whether operation should proceed without additional confirmation
    """
    # For now, we'll always return True (proceed) for simplicity
    # In a real implementation, this might check for user preferences or other factors
    return True


def update_task(session: Session, user: User, task_id: int, title: str = None, description: str = None) -> Dict[str, Any]:
    """
    MCP Tool: Update a task for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        Dictionary with updated task information
    """
    logger.info(f"MCP tool 'update_task' called for user {user.id} and task {task_id}")

    from ..models.task import TaskUpdate

    # Prepare the task update data
    task_update = TaskUpdate(
        title=title,
        description=description
    )

    # Update the task using the service
    task = task_service.update_task(session, task_id, task_update, user)

    if not task:
        logger.error(f"Failed to update task {task_id} for user {user.id}")
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found or not owned by user",
            "task_id": task_id
        }

    logger.info(f"Task {task_id} updated successfully")

    # Return the updated task information
    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "description": task.description,
        "updated_at": task.updated_at.isoformat()
    }


# Register the tools with the MCP server
mcp_server.register_tool("add_task", add_task)
mcp_server.register_tool("list_tasks", list_tasks)
mcp_server.register_tool("complete_task", complete_task)
mcp_server.register_tool("delete_task", delete_task)
mcp_server.register_tool("update_task", update_task)

logger.info("Task MCP tools registered successfully")