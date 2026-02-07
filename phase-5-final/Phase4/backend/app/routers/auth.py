from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from app.database import engine
from app.models.user import User, UserCreate, UserRead, Token, UserLogin
from app.core.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate):
    """Register a new user."""
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        db_user = User(
            email=user.email,
            name=user.name,
            hashed_password=get_password_hash(user.password)
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user and return access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return current_user