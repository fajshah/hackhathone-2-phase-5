"""
Chat API routes for the todo chatbot system.
Handles natural language processing and task management through chat interface.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session
from ..services.chat_service import ChatService
from ..services.state_service import StateService
from ..services.task_service import TaskService
from ..services.task_repository import TaskRepository
from .models import ChatMessageRequest, ChatMessageResponse


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_endpoint(
    chat_request: ChatMessageRequest,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Process a chat message from the user and return a response.

    This endpoint handles natural language processing and performs
    the appropriate actions based on the user's message.
    """
    try:
        # Initialize services
        chat_service = ChatService()
        state_service = StateService()

        # Create task service with session
        task_repo = TaskRepository(db_session)
        task_service = TaskService(task_repo)

        # Process the user message to determine intent and parameters
        parsed_result = chat_service.process_message(
            message=chat_request.message,
            user_id=chat_request.user_id
        )

        intent = parsed_result["intent"]
        parameters = parsed_result["parameters"]

        # Perform action based on intent
        actions_taken = []
        response_message = ""

        if intent == "create_task":
            if "title" in parameters:
                # Create a new task
                task_data = parameters.copy()

                # Set user_id from the request if not in parameters
                if "user_id" not in task_data:
                    task_data["user_id"] = chat_request.user_id

                # Create the task
                created_task = await task_service.create_task(task_data)

                # Add action record
                actions_taken.append({
                    "type": "task_created",
                    "task_id": created_task.id,
                    "task_title": created_task.title,
                    "timestamp": datetime.utcnow().isoformat()
                })

                response_message = f"Okay, I've created a task for '{created_task.title}'!"
            else:
                response_message = "I'm sorry, I couldn't understand what task you want to create. Could you please rephrase?"

        elif intent == "complete_task":
            # Find task by title or partial title
            if "task_identifier" in parameters:
                task_identifier = parameters["task_identifier"]

                # Find tasks for the user that match the identifier
                user_tasks = await task_service.get_tasks_for_user(
                    user_id=chat_request.user_id
                )

                # Find the task that matches the identifier
                target_task = None
                for task in user_tasks:
                    if task_identifier.lower() in task.title.lower():
                        target_task = task
                        break

                if target_task:
                    # Complete the task
                    completed_task = await task_service.complete_task(
                        task_id=target_task.id,
                        user_id=chat_request.user_id
                    )

                    if completed_task:
                        actions_taken.append({
                            "type": "task_completed",
                            "task_id": completed_task.id,
                            "task_title": completed_task.title,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        response_message = f"I've marked the task '{completed_task.title}' as complete!"
                    else:
                        response_message = "I couldn't complete that task. Are you sure you own this task?"
                else:
                    response_message = f"I couldn't find a task matching '{task_identifier}'."
            else:
                response_message = "Which task would you like to mark as complete? Please specify the task."

        elif intent == "list_tasks":
            # Get user's tasks
            user_tasks = await task_service.get_tasks_for_user(
                user_id=chat_request.user_id
            )

            if user_tasks:
                task_titles = [task.title for task in user_tasks]
                task_list_str = ", ".join(task_titles[:5])  # Show first 5 tasks
                if len(user_tasks) > 5:
                    task_list_str += f" (and {len(user_tasks) - 5} more)"

                response_message = f"You have {len(user_tasks)} tasks: {task_list_str}"
            else:
                response_message = "You don't have any tasks right now."

        elif intent == "delete_task":
            # Find and delete task by identifier
            if "task_identifier" in parameters:
                task_identifier = parameters["task_identifier"]

                # Find tasks for the user that match the identifier
                user_tasks = await task_service.get_tasks_for_user(
                    user_id=chat_request.user_id
                )

                # Find the task that matches the identifier
                target_task = None
                for task in user_tasks:
                    if task_identifier.lower() in task.title.lower():
                        target_task = task
                        break

                if target_task:
                    # Delete the task
                    success = await task_service.delete_task(
                        task_id=target_task.id,
                        user_id=chat_request.user_id
                    )

                    if success:
                        actions_taken.append({
                            "type": "task_deleted",
                            "task_id": target_task.id,
                            "task_title": target_task.title,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        response_message = f"I've deleted the task '{target_task.title}'."
                    else:
                        response_message = "I couldn't delete that task. Are you sure you own this task?"
                else:
                    response_message = f"I couldn't find a task matching '{task_identifier}'."
            else:
                response_message = "Which task would you like to delete? Please specify the task."

        elif intent == "unknown":
            # For unknown intents, provide a helpful response
            response_message = "I'm not sure I understood that. I can help you create tasks, complete tasks, list your tasks, or delete tasks. Could you rephrase your request?"

        else:
            # For other recognized intents, delegate to chat service
            response_message = chat_service.generate_response(intent, parameters)

        # Store/update conversation context if provided
        session_key = f"session:{chat_request.user_id}"
        if chat_request.context:
            # Save or update the conversation context
            await state_service.save_state(session_key, {
                "user_id": chat_request.user_id,
                "last_message": chat_request.message,
                "last_response": response_message,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            # Get existing context or create new
            context_data = await state_service.get_state(session_key) or {}
            await state_service.save_state(session_key, {
                "user_id": chat_request.user_id,
                "last_message": chat_request.message,
                "last_response": response_message,
                "timestamp": datetime.utcnow().isoformat(),
                **context_data  # Preserve any existing context
            })

        # Create the response
        response = ChatMessageResponse(
            response=response_message,
            actions=actions_taken,
            context=f"session:{chat_request.user_id}"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/chat/session", response_model=Dict[str, Any])
async def get_session_context(
    user_id: str,
    state_service: StateService = Depends()
):
    """
    Get the current conversation session context for a user.
    """
    try:
        session_key = f"session:{user_id}"
        context = await state_service.get_state(session_key)

        if context:
            return {
                "user_id": user_id,
                "context": context,
                "exists": True
            }
        else:
            return {
                "user_id": user_id,
                "context": {},
                "exists": False
            }
    except Exception as e:
        logger.error(f"Error getting session context: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session context: {str(e)}"
        )


@router.post("/chat/session/reset", response_model=Dict[str, str])
async def reset_session_context(
    user_id: str,
    state_service: StateService = Depends()
):
    """
    Reset the conversation session context for a user.
    """
    try:
        session_key = f"session:{user_id}"
        success = await state_service.delete_state(session_key)

        if success:
            return {
                "status": "success",
                "message": f"Session context reset for user {user_id}"
            }
        else:
            return {
                "status": "partial_success",  # Or success if no context existed
                "message": f"Session context reset attempted for user {user_id}"
            }
    except Exception as e:
        logger.error(f"Error resetting session context: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset session context: {str(e)}"
        )