"""Database setup - create connection and session."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from module4.config import get_settings
from module4.models import Base
settings = get_settings()

# Create engine (connection to database)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session - FastAPI uses this."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)