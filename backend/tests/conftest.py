"""
Pytest fixtures and configuration for LLMLab tests.

Sets up test database, test client, and mock data.
"""

import os
from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-for-testing-only"
os.environ["ENCRYPTION_KEY"] = "dGVzdC1lbmNyeXB0aW9uLWtleS0zMi1ieXRlcyE="  # Base64 test key
os.environ["GITHUB_CLIENT_ID"] = "test-client-id"
os.environ["GITHUB_CLIENT_SECRET"] = "test-client-secret"
os.environ["GITHUB_REDIRECT_URI"] = "http://localhost:8000/auth/github/callback"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["ENVIRONMENT"] = "test"

from database import Base, get_db
from main import app
from models import ApiKey, UsageLog, User
from security import encrypt_api_key


# =============================================================================
# DATABASE FIXTURES
# =============================================================================


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine with SQLite in-memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        github_id=12345,
        email="test@example.com",
        username="testuser",
        avatar_url="https://github.com/images/test.png",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    from auth import create_access_token

    token, _ = create_access_token(test_user.id)
    return token


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """Headers with authentication for test requests."""
    return {"Authorization": f"Bearer {test_user_token}"}


# =============================================================================
# API KEY FIXTURES
# =============================================================================


@pytest.fixture
def test_openai_key(db_session: Session, test_user: User) -> ApiKey:
    """Create a test OpenAI API key."""
    encrypted = encrypt_api_key("sk-test-openai-key-12345")
    api_key = ApiKey(
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted,
        proxy_key="llmlab_pk_test_openai_12345678",
    )
    db_session.add(api_key)
    db_session.commit()
    db_session.refresh(api_key)
    return api_key


@pytest.fixture
def test_anthropic_key(db_session: Session, test_user: User) -> ApiKey:
    """Create a test Anthropic API key."""
    encrypted = encrypt_api_key("sk-ant-test-anthropic-key-12345")
    api_key = ApiKey(
        user_id=test_user.id,
        provider="anthropic",
        encrypted_key=encrypted,
        proxy_key="llmlab_pk_test_anthropic_12345",
    )
    db_session.add(api_key)
    db_session.commit()
    db_session.refresh(api_key)
    return api_key


# =============================================================================
# USAGE LOG FIXTURES
# =============================================================================


@pytest.fixture
def test_usage_logs(db_session: Session, test_user: User) -> list[UsageLog]:
    """Create sample usage logs for testing stats."""
    logs = []
    now = datetime.utcnow()

    # Today's logs
    logs.append(
        UsageLog(
            user_id=test_user.id,
            provider="openai",
            model="gpt-4o",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.0075,
            created_at=now,
        )
    )

    # Yesterday's logs
    logs.append(
        UsageLog(
            user_id=test_user.id,
            provider="openai",
            model="gpt-4o-mini",
            input_tokens=2000,
            output_tokens=1000,
            cost_usd=0.0009,
            created_at=now - timedelta(days=1),
        )
    )

    # Last week's logs
    logs.append(
        UsageLog(
            user_id=test_user.id,
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            input_tokens=5000,
            output_tokens=2000,
            cost_usd=0.045,
            created_at=now - timedelta(days=5),
        )
    )

    # Last month's logs
    logs.append(
        UsageLog(
            user_id=test_user.id,
            provider="openai",
            model="gpt-4o",
            input_tokens=10000,
            output_tokens=5000,
            cost_usd=0.075,
            created_at=now - timedelta(days=20),
        )
    )

    for log in logs:
        db_session.add(log)
    db_session.commit()

    return logs
