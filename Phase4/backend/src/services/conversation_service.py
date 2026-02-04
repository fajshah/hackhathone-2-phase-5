"""
Conversation service for the Todo AI Chatbot.
Handles CRUD operations for Conversation model with proper user authorization.
"""
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.conversation import Conversation, ConversationCreate, ConversationUpdate
from ..models.user import User
from ..models.message import Message
from datetime import datetime


class ConversationService:
    """
    Service class for handling conversation-related operations.
    Implements CRUD operations with proper user authorization.
    """

    @staticmethod
    def create_conversation(session: Session, conversation_create: ConversationCreate, user: User) -> Conversation:
        """
        Create a new conversation for the authenticated user.
        Verifies that the conversation is being created for the correct user.
        """
        # Verify that the user_id in the request matches the authenticated user
        if conversation_create.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create conversation for this user"
            )

        # Create the conversation instance
        conversation = Conversation(
            title=conversation_create.title,
            description=conversation_create.description,
            user_id=user.id
        )

        # Add to session and commit
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: int, user: User) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID for the authenticated user.
        Returns None if the conversation doesn't exist or doesn't belong to the user.
        """
        # Query for the conversation belonging to the user
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conversation = session.exec(statement).first()
        return conversation

    @staticmethod
    def get_conversations_by_user(
        session: Session,
        user: User,
        limit: int = 100,
        offset: int = 0,
        is_active: Optional[bool] = None
    ) -> List[Conversation]:
        """
        Retrieve all conversations for the authenticated user with optional filtering.
        """
        # Start with a base query for conversations belonging to the user
        statement = select(Conversation).where(Conversation.user_id == user.id)

        # Apply active status filter if provided
        if is_active is not None:
            statement = statement.where(Conversation.is_active == is_active)

        # Apply pagination
        statement = statement.offset(offset).limit(limit)

        # Execute query
        conversations = session.exec(statement).all()
        return conversations

    @staticmethod
    def update_conversation(
        session: Session,
        conversation_id: int,
        conversation_update: ConversationUpdate,
        user: User
    ) -> Optional[Conversation]:
        """
        Update a conversation for the authenticated user.
        Returns the updated conversation or None if it doesn't exist or doesn't belong to the user.
        """
        # Get the existing conversation
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user)
        if not conversation:
            return None

        # Update the conversation with the provided fields
        update_data = conversation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        # Update the timestamp
        conversation.updated_at = datetime.utcnow()

        # Commit changes
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    @staticmethod
    def delete_conversation(session: Session, conversation_id: int, user: User) -> bool:
        """
        Delete a conversation for the authenticated user.
        Returns True if the conversation was deleted, False if it didn't exist or didn't belong to the user.
        """
        # Get the conversation to delete
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user)
        if not conversation:
            return False

        # Delete the conversation
        session.delete(conversation)
        session.commit()

        return True

    @staticmethod
    def deactivate_conversation(session: Session, conversation_id: int, user: User) -> Optional[Conversation]:
        """
        Mark a conversation as inactive for the authenticated user.
        Returns the updated conversation or None if it doesn't exist or doesn't belong to the user.
        """
        # Get the conversation to update
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user)
        if not conversation:
            return None

        # Mark as inactive
        conversation.deactivate()

        # Commit changes
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    @staticmethod
    def get_active_conversations_count(session: Session, user: User) -> int:
        """
        Get the count of active conversations for the authenticated user.
        """
        statement = select(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.is_active == True
        )
        conversations = session.exec(statement).all()
        return len(conversations)

    @staticmethod
    def get_conversation_history(session: Session, conversation_id: int, user: User, limit: Optional[int] = 50) -> List[Message]:
        """
        Get the full history of messages for a conversation with proper user authorization.
        """
        # First verify that the user has access to this conversation
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user)
        if not conversation:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this conversation"
            )

        # Query for messages in this conversation ordered by creation time
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        # Apply limit if specified
        if limit:
            statement = statement.limit(limit)

        messages = session.exec(statement).all()
        return messages


# Create a singleton instance of the service
conversation_service = ConversationService()