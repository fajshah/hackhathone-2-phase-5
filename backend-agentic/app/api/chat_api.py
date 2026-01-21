from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
import os
from app.db.session import get_session
from app.models.conversation import Conversation, Message, ConversationCreate
from app.models.user import User
from app.agents.todo_agent import get_agent
from datetime import datetime

def chat_endpoint(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint that processes user messages through the AI agent
    """
    # Validate user exists
    try:
        user_uuid = UUID(user_id)
        user = session.get(User, user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Get or create conversation
    conversation = None
    if conversation_id:
        try:
            conv_uuid = UUID(conversation_id)
            conversation = session.get(Conversation, conv_uuid)
            if not conversation or str(conversation.user_id) != user_id:
                raise HTTPException(status_code=404, detail="Conversation not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation ID format")

    # If no conversation was found or provided, create a new one
    if not conversation:
        conv_create = ConversationCreate(title=f"Chat with {user.name}")
        conversation = Conversation.model_validate(conv_create)
        conversation.user_id = user_uuid
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Create and store user message
    user_message = Message(
        role="user",
        content=message,
        conversation_id=conversation.id
    )
    session.add(user_message)
    session.commit()

    # Get conversation history for the agent
    history_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc())
    history = session.exec(history_query).all()

    # Format history for the agent
    formatted_history = []
    for msg in history[:-1]:  # Exclude the current message we just added
        formatted_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # Process message through the agent
    agent = get_agent()
    ai_response = agent.process_message(
        user_message=message,
        user_id=user_id,
        conversation_history=formatted_history
    )

    # Create and store AI response message
    ai_message = Message(
        role="assistant",
        content=ai_response,
        conversation_id=conversation.id
    )
    session.add(ai_message)
    session.commit()

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    return {
        "conversation_id": str(conversation.id),
        "response": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_user_conversations(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Get all conversations for a user
    """
    try:
        user_uuid = UUID(user_id)
        # Verify user exists
        user = session.get(User, user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's conversations
        from sqlmodel import desc
        conversations = session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_uuid)
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
        ).all()

        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "is_active": conv.is_active
                }
                for conv in conversations
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Get all messages for a specific conversation
    """
    try:
        conv_uuid = UUID(conversation_id)
        conversation = session.get(Conversation, conv_uuid)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get messages from the conversation
        from sqlmodel import desc
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(desc(Message.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

        return {
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")