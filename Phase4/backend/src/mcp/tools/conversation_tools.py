"""
MCP tools for conversation operations in the Todo AI Chatbot.
Contains tools for creating, managing, and retrieving conversations.
"""
from typing import Dict, Any
from sqlmodel import Session
from ...models.conversation import Conversation, ConversationCreate
from ...models.message import Message, MessageCreate
from ...models.user import User
from ...services.conversation_service import conversation_service
from ...services.message_service import message_service
from ..server import mcp_server
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_conversation(session: Session, user: User, title: str = None, description: str = None) -> Dict[str, Any]:
    """
    MCP Tool: Create a new conversation for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        title: Optional conversation title
        description: Optional conversation description

    Returns:
        Dictionary with conversation information
    """
    logger.info(f"MCP tool 'create_conversation' called for user {user.id}")

    # Prepare the conversation creation data
    conversation_create = ConversationCreate(
        title=title,
        description=description,
        user_id=user.id
    )

    # Create the conversation using the service
    conversation = conversation_service.create_conversation(session, conversation_create, user)

    logger.info(f"Conversation created successfully with ID {conversation.id}")

    # Return the created conversation information
    return {
        "conversation_id": conversation.id,
        "uuid": conversation.uuid,
        "title": conversation.title,
        "description": conversation.description,
        "created_at": conversation.created_at.isoformat(),
        "is_active": conversation.is_active
    }


def get_conversation_history(session: Session, user: User, conversation_id: int) -> Dict[str, Any]:
    """
    MCP Tool: Get conversation history for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        conversation_id: ID of the conversation to retrieve

    Returns:
        Dictionary with conversation and message history
    """
    logger.info(f"MCP tool 'get_conversation_history' called for user {user.id} and conversation {conversation_id}")

    # Get the conversation using the service
    conversation = conversation_service.get_conversation_by_id(session, conversation_id, user)

    if not conversation:
        logger.error(f"Conversation {conversation_id} not found for user {user.id}")
        return {
            "success": False,
            "error": f"Conversation with ID {conversation_id} not found or not owned by user",
            "conversation_id": conversation_id
        }

    # Get messages for the conversation
    messages = message_service.get_messages_by_conversation(session, conversation_id, user)

    logger.info(f"Retrieved conversation {conversation_id} with {len(messages)} messages for user {user.id}")

    # Format messages for return
    messages_list = []
    for message in messages:
        messages_list.append({
            "message_id": message.id,
            "role": message.role.value,
            "content": message.content,
            "sequence_number": message.sequence_number,
            "created_at": message.created_at.isoformat()
        })

    return {
        "success": True,
        "conversation_id": conversation.id,
        "title": conversation.title,
        "description": conversation.description,
        "created_at": conversation.created_at.isoformat(),
        "messages": messages_list,
        "message_count": len(messages_list)
    }


def store_message(session: Session, user: User, conversation_id: int, role: str, content: str) -> Dict[str, Any]:
    """
    MCP Tool: Store a message in a conversation for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        conversation_id: ID of the conversation
        role: Role of the message sender (user, assistant, system)
        content: Content of the message

    Returns:
        Dictionary with stored message information
    """
    logger.info(f"MCP tool 'store_message' called for user {user.id}, conversation {conversation_id}, role {role}")

    # Validate role
    from ..models.message import MessageRole
    try:
        role_enum = MessageRole(role.lower())
    except ValueError:
        logger.error(f"Invalid message role: {role}")
        return {
            "success": False,
            "error": f"Invalid role: {role}. Valid roles are: {', '.join([r.value for r in MessageRole])}",
            "conversation_id": conversation_id
        }

    # Prepare the message creation data
    message_create = MessageCreate(
        role=role_enum,
        content=content,
        user_id=user.id,
        conversation_id=conversation_id
    )

    # Create the message using the service
    message = message_service.create_message(session, message_create, user)

    logger.info(f"Message stored successfully with ID {message.id} in conversation {conversation_id}")

    # Return the created message information
    return {
        "success": True,
        "message_id": message.id,
        "conversation_id": conversation_id,
        "role": message.role.value,
        "content": message.content,
        "sequence_number": message.sequence_number,
        "created_at": message.created_at.isoformat()
    }


def get_recent_conversations(session: Session, user: User, limit: int = 10) -> Dict[str, Any]:
    """
    MCP Tool: Get recent conversations for the authenticated user.

    Args:
        session: Database session
        user: Authenticated user
        limit: Number of recent conversations to retrieve

    Returns:
        Dictionary with list of recent conversations
    """
    logger.info(f"MCP tool 'get_recent_conversations' called for user {user.id}, limit {limit}")

    # Get conversations using the service
    conversations = conversation_service.get_conversations_by_user(session, user, limit=limit)

    logger.info(f"Retrieved {len(conversations)} recent conversations for user {user.id}")

    # Format conversations for return
    conversations_list = []
    for conversation in conversations:
        conversations_list.append({
            "conversation_id": conversation.id,
            "title": conversation.title,
            "description": conversation.description,
            "created_at": conversation.created_at.isoformat(),
            "is_active": conversation.is_active
        })

    return {
        "conversations": conversations_list,
        "total_count": len(conversations_list),
        "limit": limit
    }


# Register the tools with the MCP server
mcp_server.register_tool("create_conversation", create_conversation)
mcp_server.register_tool("get_conversation_history", get_conversation_history)
mcp_server.register_tool("store_message", store_message)
mcp_server.register_tool("get_recent_conversations", get_recent_conversations)

logger.info("Conversation MCP tools registered successfully")