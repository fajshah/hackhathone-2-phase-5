from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc
from typing import List
from uuid import UUID
from app.database import engine
from app.models.todo import Todo, TodoCreate, TodoRead, TodoUpdate
from app.models.user import User
from app.core.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=TodoRead)
def create_todo(todo: TodoCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new todo item."""
    with Session(engine) as session:
        db_todo = Todo.model_validate(todo)
        db_todo.owner_id = current_user.id
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo

@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(todo_id: UUID, current_user: User = Depends(get_current_active_user)):
    """Get a specific todo item."""
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id, Todo.owner_id == current_user.id)
        todo = session.exec(statement).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

@router.get("/", response_model=List[TodoRead])
def read_todos(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """Get all todos for the current user."""
    with Session(engine) as session:
        statement = select(Todo).where(Todo.owner_id == current_user.id).order_by(desc(Todo.created_at))
        todos = session.exec(statement.offset(skip).limit(limit)).all()
        return todos

@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: UUID,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific todo item."""
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id, Todo.owner_id == current_user.id)
        db_todo = session.exec(statement).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Update fields
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todo, field, value)

        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo

@router.delete("/{todo_id}")
def delete_todo(todo_id: UUID, current_user: User = Depends(get_current_active_user)):
    """Delete a specific todo item."""
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id, Todo.owner_id == current_user.id)
        db_todo = session.exec(statement).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        session.delete(db_todo)
        session.commit()
        return {"message": "Todo deleted successfully"}