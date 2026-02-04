"""
Chat API endpoint for the Todo AI Chatbot.
Handles user requests and orchestrates the AI agent response.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from ..agents.todo_agent import todo_agent
from ..auth import AuthService, get_current_user
from ..models.user import User
from ..mcp.server import mcp_server
from ..services.conversation_service import conversation_service
from ..services.message_service import message_service
from ..database import get_session
from sqlmodel import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.
    """
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    """
    conversation_id: int
    response: str
    tool_calls: list
    success: bool


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint for the Todo AI Chatbot.

    This endpoint:
    1. Receives a user message and optional conversation ID
    2. Processes the message through the AI agent
    3. Executes any required MCP tools
    4. Stores the user and assistant messages
    5. Returns the AI's response

    Args:
        request: ChatRequest containing the user message and optional conversation ID
        current_user: The authenticated user making the request
        session: Database session for database operations

    Returns:
        ChatResponse with conversation ID, AI response, and any tool calls made
    """
    logger.info(f"Received chat request from user {current_user.id}")

    try:
        # If no conversation_id is provided, create a new conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            # Create a new conversation
            from ..models.conversation import ConversationCreate
            conversation_create = ConversationCreate(
                title=f"Conversation with {current_user.email}",
                description="Auto-generated conversation",
                user_id=current_user.id
            )

            # Use the conversation service to create the conversation
            from sqlmodel import select
            new_conversation = conversation_service.create_conversation(
                session=session,
                conversation_create=conversation_create,
                user=current_user
            )
            conversation_id = new_conversation.id

            logger.info(f"Created new conversation with ID {conversation_id}")
        else:
            # Verify that the conversation belongs to the user
            conversation = conversation_service.get_conversation_by_id(
                session=session,
                conversation_id=conversation_id,
                user=current_user
            )
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found or does not belong to user"
                )

        # Store the user's message in the conversation
        from ..models.message import MessageCreate, MessageRole
        user_message = MessageCreate(
            role=MessageRole.USER,
            content=request.message,
            user_id=current_user.id,
            conversation_id=conversation_id
        )

        # Use the message service to store the message
        stored_message = message_service.create_message(
            session=session,
            message_create=user_message,
            user=current_user
        )

        logger.info(f"Stored user message with ID {stored_message.id}")

        # Process the request through the AI agent
        # We need to create a token for the MCP server to use
        user_token = AuthService.create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email}
        )

        agent_response = todo_agent.process_request(
            session=session,
            user_input=request.message,
            user_token=user_token,
            conversation_id=conversation_id
        )

        # Store the assistant's response in the conversation
        from ..models.message import MessageCreate, MessageRole
        assistant_message = MessageCreate(
            role=MessageRole.ASSISTANT,
            content=agent_response.get("response", "No response"),
            user_id=current_user.id,  # This would typically be an assistant ID, but we'll use user ID for now
            conversation_id=conversation_id
        )

        # Use the message service to store the assistant message
        assistant_stored_message = message_service.create_message(
            session=session,
            message_create=assistant_message,
            user=current_user
        )

        logger.info(f"Stored assistant message with ID {assistant_stored_message.id}")

        # Prepare the response
        response = ChatResponse(
            conversation_id=conversation_id,
            response=agent_response.get("response", "I processed your request."),
            tool_calls=agent_response.get("tool_calls", []),
            success=True
        )

        logger.info(f"Returning chat response for conversation {conversation_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific conversation and its messages.

    Args:
        conversation_id: ID of the conversation to retrieve
        current_user: The authenticated user making the request
        session: Database session for database operations

    Returns:
        Dictionary with conversation details and messages
    """
    logger.info(f"Retrieving conversation {conversation_id} for user {current_user.id}")

    try:
        # Verify that the conversation belongs to the user
        conversation = conversation_service.get_conversation_by_id(
            session=session,
            conversation_id=conversation_id,
            user=current_user
        )
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or does not belong to user"
            )

        # Get messages for the conversation
        messages = message_service.get_messages_by_conversation(
            session=session,
            conversation_id=conversation_id,
            user=current_user
        )

        # Format the response
        conversation_data = {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "description": conversation.description,
            "created_at": conversation.created_at.isoformat(),
            "is_active": conversation.is_active,
            "messages": [
                {
                    "message_id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "sequence_number": msg.sequence_number,
                    "created_at": msg.created_at.isoformat()
                } for msg in messages
            ],
            "message_count": len(messages)
        }

        logger.info(f"Retrieved conversation {conversation_id} with {len(messages)} messages")
        return conversation_data

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving the conversation"
        )


@router.get("/conversations")
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve all conversations for the authenticated user.

    Args:
        current_user: The authenticated user making the request
        session: Database session for database operations

    Returns:
        List of user's conversations
    """
    logger.info(f"Retrieving conversations for user {current_user.id}")

    try:
        # Get all conversations for the user
        conversations = conversation_service.get_conversations_by_user(
            session=session,
            user=current_user
        )

        # Format the response
        conversations_data = [
            {
                "conversation_id": conv.id,
                "title": conv.title,
                "description": conv.description,
                "created_at": conv.created_at.isoformat(),
                "is_active": conv.is_active
            } for conv in conversations
        ]

        logger.info(f"Retrieved {len(conversations_data)} conversations for user {current_user.id}")
        return {
            "conversations": conversations_data,
            "total_count": len(conversations_data)
        }

    except Exception as e:
        logger.error(f"Error retrieving conversations for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving conversations"
        )


logger.info("Chat API endpoints registered successfully")