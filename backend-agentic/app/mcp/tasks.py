from sqlmodel import Session, select
from typing import Dict, Any, List
from datetime import datetime
from app.db.session import engine
from app.models.task import Task, TaskCreate, Status
from app.mcp.registry import mcp_registry
from uuid import UUID

@mcp_registry.register_tool(
    name="add_task",
    description="Add a new task to the user's task list",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "title": {"type": "string", "description": "The title of the task"},
            "description": {"type": "string", "description": "The description of the task"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "The priority of the task"},
            "due_date": {"type": "string", "format": "date-time", "description": "Due date for the task"},
            "category": {"type": "string", "description": "Category of the task"}
        },
        "required": ["user_id", "title"]
    }
)
def add_task_tool(user_id: str, title: str, description: str = None, priority: str = "medium", due_date: str = None, category: str = None) -> Dict[str, Any]:
    """
    MCP tool to add a new task to the user's task list
    """
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)

        # Create task object
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "user_id": user_uuid
        }

        # Remove None values
        task_data = {k: v for k, v in task_data.items() if v is not None}

        task_create = TaskCreate(**task_data)

        # Create task in database
        with Session(engine) as session:
            db_task = Task.model_validate(task_create)
            db_task.user_id = user_uuid
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            # Return success response
            return {
                "success": True,
                "task_id": str(db_task.id),
                "message": f"Task '{db_task.title}' added successfully",
                "task": {
                    "id": str(db_task.id),
                    "title": db_task.title,
                    "description": db_task.description,
                    "priority": db_task.priority.value,
                    "status": db_task.status.value,
                    "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
                    "category": db_task.category,
                    "created_at": db_task.created_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add task"
        }


@mcp_registry.register_tool(
    name="list_tasks",
    description="List tasks for a user with optional filtering",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "status_filter": {"type": "string", "enum": ["all", "todo", "in_progress", "done"], "description": "Filter tasks by status"}
        },
        "required": ["user_id"]
    }
)
def list_tasks_tool(user_id: str, status_filter: str = "all") -> Dict[str, Any]:
    """
    MCP tool to list tasks for a user with optional filtering
    """
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)

        with Session(engine) as session:
            # Build query based on status filter
            query = select(Task).where(Task.user_id == user_uuid)

            if status_filter != "all":
                if status_filter == "todo":
                    query = query.where(Task.status == Status.TODO)
                elif status_filter == "in_progress":
                    query = query.where(Task.status == Status.IN_PROGRESS)
                elif status_filter == "done":
                    query = query.where(Task.status == Status.DONE)

            # Execute query
            tasks = session.exec(query.order_by(Task.created_at.desc())).all()

            # Format tasks for response
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "category": task.category,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                })

            return {
                "success": True,
                "count": len(formatted_tasks),
                "tasks": formatted_tasks,
                "filter": status_filter
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list tasks"
        }


@mcp_registry.register_tool(
    name="complete_task",
    description="Mark a task as completed",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "string", "description": "The ID of the task to complete"}
        },
        "required": ["user_id", "task_id"]
    }
)
def complete_task_tool(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool to mark a task as completed
    """
    try:
        # Convert IDs to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        with Session(engine) as session:
            # Find the task
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": "Task not found or does not belong to user"
                }

            # Update task status to done
            task.status = Status.DONE
            task.completed_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' marked as completed",
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "status": task.status.value,
                    "completed_at": task.completed_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to complete task"
        }


@mcp_registry.register_tool(
    name="delete_task",
    description="Delete a task from the user's task list",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "string", "description": "The ID of the task to delete"}
        },
        "required": ["user_id", "task_id"]
    }
)
def delete_task_tool(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool to delete a task from the user's task list
    """
    try:
        # Convert IDs to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        with Session(engine) as session:
            # Find the task
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": "Task not found or does not belong to user"
                }

            # Delete the task
            session.delete(task)
            session.commit()

            return {
                "success": True,
                "message": f"Task '{task.title}' deleted successfully",
                "deleted_task_id": str(task.id)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete task"
        }


@mcp_registry.register_tool(
    name="update_task",
    description="Update properties of a task",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "string", "description": "The ID of the task to update"},
            "title": {"type": "string", "description": "New title for the task"},
            "description": {"type": "string", "description": "New description for the task"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority for the task"},
            "status": {"type": "string", "enum": ["todo", "in_progress", "done"], "description": "New status for the task"},
            "due_date": {"type": "string", "format": "date-time", "description": "New due date for the task"},
            "category": {"type": "string", "description": "New category for the task"}
        },
        "required": ["user_id", "task_id"]
    }
)
def update_task_tool(user_id: str, task_id: str, **updates) -> Dict[str, Any]:
    """
    MCP tool to update properties of a task
    """
    try:
        # Convert IDs to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Remove None values from updates
        updates = {k: v for k, v in updates.items() if v is not None}

        with Session(engine) as session:
            # Find the task
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": "Task not found or does not belong to user"
                }

            # Update task properties
            for field, value in updates.items():
                if hasattr(task, field):
                    setattr(task, field, value)

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully",
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "category": task.category,
                    "updated_at": task.updated_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update task"
        }