from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc
from typing import List
from uuid import UUID
from app.database import engine
from app.models.conversation import Conversation, ConversationCreate, ConversationRead, ConversationUpdate
from app.models.user import User
from app.core.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ConversationRead)
def create_conversation(
    conversation: ConversationCreate, 
    current_user: User = Depends(get_current_active_user)
):
    """Create a new conversation."""
    with Session(engine) as session:
        db_conversation = Conversation.model_validate(conversation)
        db_conversation.user_id = current_user.id
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)
        return db_conversation

@router.get("/{conversation_id}", response_model=ConversationRead)
def read_conversation(
    conversation_id: UUID, 
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific conversation."""
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == current_user.id
        )
        conversation = session.exec(statement).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

@router.get("/", response_model=List[ConversationRead])
def read_conversations(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user)
):
    """Get all conversations for the current user."""
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.user_id == current_user.id
        ).order_by(desc(Conversation.updated_at))
        conversations = session.exec(statement.offset(skip).limit(limit)).all()
        return conversations

@router.patch("/{conversation_id}", response_model=ConversationRead)
def update_conversation(
    conversation_id: UUID, 
    conversation_update: ConversationUpdate, 
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific conversation."""
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == current_user.id
        )
        db_conversation = session.exec(statement).first()
        if not db_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update fields
        update_data = conversation_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_conversation, field, value)
        
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)
        return db_conversation

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: UUID, 
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific conversation."""
    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == current_user.id
        )
        db_conversation = session.exec(statement).first()
        if not db_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        session.delete(db_conversation)
        session.commit()
        return {"message": "Conversation deleted successfully"}