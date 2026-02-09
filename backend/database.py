"""
Database connection and session management.

Uses SQLAlchemy with Supabase PostgreSQL.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from config import get_settings

# Create base class for models
Base = declarative_base()


def get_engine():
    """
    Create database engine with connection pooling.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=not settings.is_production,
    )


# Create engine and session factory
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.

    Yields:
        Session: Database session that auto-closes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
