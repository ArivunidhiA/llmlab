"""Database connection and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator
import os

from config import settings

# For local development with PostgreSQL
DATABASE_URL = settings.database_url

# For Supabase (if configured)
if settings.supabase_url and settings.supabase_key:
    # Construct direct PostgreSQL connection string from Supabase
    DATABASE_URL = f"postgresql://postgres:{settings.supabase_key}@{settings.supabase_url.replace('https://', '')}/postgres"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    poolclass=NullPool,  # Disable connection pooling for serverless
    pool_pre_ping=True,  # Check connections before use
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
