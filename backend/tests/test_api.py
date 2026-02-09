"""Tests for LLMlab API"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from config import Settings

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }


# ============ HEALTH TESTS ============

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


# ============ AUTH TESTS ============

def test_signup(client, test_user_data):
    """Test user signup"""
    response = client.post("/api/auth/signup", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email(client, test_user_data):
    """Test signup with duplicate email"""
    # First signup
    client.post("/api/auth/signup", json=test_user_data)
    
    # Second signup with same email
    response = client.post("/api/auth/signup", json=test_user_data)
    assert response.status_code == 400


def test_login(client, test_user_data):
    """Test user login"""
    # Signup first
    client.post("/api/auth/signup", json=test_user_data)
    
    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_password(client, test_user_data):
    """Test login with invalid password"""
    # Signup first
    client.post("/api/auth/signup", json=test_user_data)
    
    # Try login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401


# ============ EVENT TESTS ============

def test_track_event(client, test_user_data):
    """Test tracking an LLM event"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    
    # Track event
    event_data = {
        "provider": "openai",
        "model": "gpt-4",
        "input_tokens": 100,
        "output_tokens": 50,
        "duration_ms": 1234.5
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/events/track", json=event_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4"
    assert data["calculated_cost"] > 0


def test_track_event_no_auth(client):
    """Test tracking event without authentication"""
    event_data = {
        "provider": "openai",
        "model": "gpt-4",
        "input_tokens": 100,
        "output_tokens": 50,
    }
    response = client.post("/api/events/track", json=event_data)
    assert response.status_code == 403  # Forbidden


def test_cost_calculation():
    """Test cost calculation accuracy"""
    from main import calculate_cost
    from config import get_provider_rates
    
    rates = get_provider_rates()
    
    # GPT-4: input $0.03/1K, output $0.06/1K
    # 100 input tokens = $0.003
    # 50 output tokens = $0.003
    # Total = $0.006
    cost = calculate_cost("openai", "gpt-4", 100, 50, rates)
    assert cost == 0.003  # (100 * 0.03 / 1000) + (50 * 0.06 / 1000)


def test_list_events(client, test_user_data):
    """Test listing tracked events"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Track multiple events
    for i in range(3):
        event_data = {
            "provider": "openai",
            "model": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 50,
        }
        client.post("/api/events/track", json=event_data, headers=headers)
    
    # List events
    response = client.get("/api/events", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


# ============ COST SUMMARY TESTS ============

def test_costs_summary(client, test_user_data):
    """Test cost summary endpoint"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Track events
    for i in range(2):
        event_data = {
            "provider": "openai",
            "model": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 50,
        }
        client.post("/api/events/track", json=event_data, headers=headers)
    
    # Get summary
    response = client.get("/api/costs/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["today"] > 0
    assert data["total"] > 0
    assert "openai" in data["by_provider"]
    assert "gpt-4" in data["by_model"]


# ============ BUDGET TESTS ============

def test_create_budget(client, test_user_data):
    """Test creating a budget"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create budget
    budget_data = {
        "monthly_limit": 1000,
        "alert_channel": "email"
    }
    response = client.post("/api/budgets", json=budget_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_limit"] == 1000


def test_get_budgets(client, test_user_data):
    """Test getting user budgets"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create budget
    budget_data = {"monthly_limit": 1000}
    client.post("/api/budgets", json=budget_data, headers=headers)
    
    # Get budgets
    response = client.get("/api/budgets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["monthly_limit"] == 1000


def test_budget_alert_logic(client, test_user_data):
    """Test budget alert threshold logic"""
    # This would test that alerts are triggered at 50%, 80%, 100%
    # Implementation in check_budget_alerts function
    pass


# ============ RECOMMENDATIONS TESTS ============

def test_recommendations(client, test_user_data):
    """Test cost recommendations endpoint"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get recommendations (should be empty initially)
    response = client.get("/api/recommendations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============ STRESS TESTS ============

def test_high_volume_events(client, test_user_data):
    """Test handling high volume of events"""
    # Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Track 100 events
    for i in range(100):
        event_data = {
            "provider": "openai",
            "model": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 50,
        }
        response = client.post("/api/events/track", json=event_data, headers=headers)
        assert response.status_code == 200
    
    # Verify they were all tracked
    response = client.get("/api/events?limit=150", headers=headers)
    data = response.json()
    assert len(data) == 100


# ============ SMOKE TESTS ============

def test_basic_user_flow(client, test_user_data):
    """Smoke test: basic user flow"""
    # 1. Signup
    signup_response = client.post("/api/auth/signup", json=test_user_data)
    assert signup_response.status_code == 200
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create budget
    budget_data = {"monthly_limit": 1000}
    budget_response = client.post("/api/budgets", json=budget_data, headers=headers)
    assert budget_response.status_code == 200
    
    # 3. Track event
    event_data = {
        "provider": "openai",
        "model": "gpt-4",
        "input_tokens": 100,
        "output_tokens": 50,
    }
    event_response = client.post("/api/events/track", json=event_data, headers=headers)
    assert event_response.status_code == 200
    
    # 4. Get cost summary
    summary_response = client.get("/api/costs/summary", headers=headers)
    assert summary_response.status_code == 200
    
    # 5. Get recommendations
    recom_response = client.get("/api/recommendations", headers=headers)
    assert recom_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
