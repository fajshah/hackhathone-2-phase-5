"""
Message service for the Todo AI Chatbot.
Handles CRUD operations for Message model with proper user authorization.
"""
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.message import Message, MessageCreate, MessageUpdate
from ..models.user import User
from ..models.conversation import Conversation
from datetime import datetime


class MessageService:
    """
    Service class for handling message-related operations.
    Implements CRUD operations with proper user authorization.
    """

    @staticmethod
    def create_message(session: Session, message_create: MessageCreate, user: User) -> Message:
        """
        Create a new message for the authenticated user.
        Verifies that the user is authorized to add a message to the conversation.
        """
        # Verify that the user_id in the request matches the authenticated user
        if message_create.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create message for this user"
            )

        # Verify that the user has access to the conversation
        conversation_statement = select(Conversation).where(
            Conversation.id == message_create.conversation_id,
            Conversation.user_id == user.id
        )
        conversation = session.exec(conversation_statement).first()
        if not conversation:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to add message to this conversation"
            )

        # Create the message instance
        message = Message(
            role=message_create.role,
            content=message_create.content,
            user_id=user.id,
            conversation_id=message_create.conversation_id
        )

        # Set sequence number based on existing messages in the conversation
        last_message_statement = select(Message).where(
            Message.conversation_id == message_create.conversation_id
        ).order_by(Message.sequence_number.desc()).limit(1)
        last_message = session.exec(last_message_statement).first()
        message.sequence_number = (last_message.sequence_number + 1) if last_message else 1

        # Add to session and commit
        session.add(message)
        session.commit()
        session.refresh(message)

        return message

    @staticmethod
    def get_message_by_id(session: Session, message_id: int, user: User) -> Optional[Message]:
        """
        Retrieve a message by its ID for the authenticated user.
        Returns None if the message doesn't exist or doesn't belong to the user.
        """
        # Query for the message belonging to the user
        statement = select(Message).where(
            Message.id == message_id,
            Message.user_id == user.id
        )
        message = session.exec(statement).first()
        return message

    @staticmethod
    def get_messages_by_conversation(
        session: Session,
        conversation_id: int,
        user: User,
        limit: int = 100,
        offset: int = 0,
        role: Optional[str] = None
    ) -> List[Message]:
        """
        Retrieve all messages for a conversation with optional filtering.
        Verifies that the user has access to the conversation.
        """
        # First verify that the user has access to the conversation
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conversation = session.exec(conversation_statement).first()
        if not conversation:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access messages in this conversation"
            )

        # Query for messages in the conversation
        statement = select(Message).where(Message.conversation_id == conversation_id)

        # Apply role filter if provided
        if role:
            statement = statement.where(Message.role == role)

        # Apply pagination
        statement = statement.order_by(Message.sequence_number).offset(offset).limit(limit)

        # Execute query
        messages = session.exec(statement).all()
        return messages

    @staticmethod
    def get_latest_messages(
        session: Session,
        user: User,
        limit: int = 10
    ) -> List[Message]:
        """
        Retrieve the latest messages across all conversations for the authenticated user.
        """
        # Query for messages belonging to the user's conversations
        statement = (
            select(Message)
            .join(Conversation)
            .where(Conversation.user_id == user.id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        # Execute query
        messages = session.exec(statement).all()
        return messages

    @staticmethod
    def update_message(session: Session, message_id: int, message_update: MessageUpdate, user: User) -> Optional[Message]:
        """
        Update a message for the authenticated user.
        Returns the updated message or None if it doesn't exist or doesn't belong to the user.
        """
        # Get the existing message
        message = MessageService.get_message_by_id(session, message_id, user)
        if not message:
            return None

        # Update the message with the provided fields
        update_data = message_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(message, field, value)

        # Update the timestamp
        message.updated_at = datetime.utcnow()

        # Commit changes
        session.add(message)
        session.commit()
        session.refresh(message)

        return message

    @staticmethod
    def delete_message(session: Session, message_id: int, user: User) -> bool:
        """
        Delete a message for the authenticated user.
        Returns True if the message was deleted, False if it didn't exist or didn't belong to the user.
        """
        # Get the message to delete
        message = MessageService.get_message_by_id(session, message_id, user)
        if not message:
            return False

        # Delete the message
        session.delete(message)
        session.commit()

        return True

    @staticmethod
    def get_messages_count(session: Session, conversation_id: int, user: User) -> int:
        """
        Get the count of messages in a conversation for the authenticated user.
        Verifies that the user has access to the conversation.
        """
        # First verify that the user has access to the conversation
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conversation = session.exec(conversation_statement).first()
        if not conversation:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access messages in this conversation"
            )

        # Count messages in the conversation
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(statement).all()
        return len(messages)


# Create a singleton instance of the service
message_service = MessageService()