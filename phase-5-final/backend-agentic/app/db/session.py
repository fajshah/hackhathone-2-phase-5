from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - using Neon PostgreSQL
DATABASE_URL = os.getenv("NEON_DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///./todo_ai.db"))

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)

def get_session():
    with Session(engine) as session:
        yield session