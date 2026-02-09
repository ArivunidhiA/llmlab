"""
LLMLab Backend Tests
Unit, integration, and smoke tests
"""

import pytest
import json
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, calculate_cost, User, CostEvent, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_TEST_URL = "sqlite:///./test_llmlab.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})

# Create tables
from main import Base
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[SessionLocal] = TestingSessionLocal

client = TestClient(app)

# ============================================================================
# UNIT TESTS - Cost Calculation
# ============================================================================

class TestCostCalculation:
    
    def test_openai_gpt4_cost(self):
        """Test GPT-4 cost calculation"""
        cost = calculate_cost("openai", "gpt-4", 1000, 500)
        # (1000/1000)*0.03 + (500/1000)*0.06 = 0.03 + 0.03 = 0.06
        assert cost == 0.06
    
    def test_anthropic_claude_cost(self):
        """Test Claude cost calculation"""
        cost = calculate_cost("anthropic", "claude-3-opus", 1000, 500)
        # (1000/1000)*0.015 + (500/1000)*0.075 = 0.015 + 0.0375 = 0.0525
        assert abs(cost - 0.0525) < 0.0001
    
    def test_google_gemini_cost(self):
        """Test Gemini cost calculation"""
        cost = calculate_cost("google", "gemini-pro", 1000, 500)
        expected = (1000/1000)*0.00025 + (500/1000)*0.0005
        assert abs(cost - expected) < 0.00001
    
    def test_zero_tokens(self):
        """Test with zero tokens"""
        cost = calculate_cost("openai", "gpt-4", 0, 0)
        assert cost == 0
    
    def test_invalid_model(self):
        """Test with invalid model (should return 0)"""
        cost = calculate_cost("openai", "invalid-model", 1000, 500)
        assert cost == 0

# ============================================================================
# INTEGRATION TESTS - API Endpoints
# ============================================================================

class TestAuthEndpoints:
    
    def test_signup(self):
        """Test user signup"""
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "api_key" in data
        assert data["api_key"].startswith("llmlab_")
    
    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        client.post(
            "/api/auth/signup",
            json={"email": "duplicate@example.com", "password": "pass"}
        )
        response = client.post(
            "/api/auth/signup",
            json={"email": "duplicate@example.com", "password": "pass"}
        )
        assert response.status_code == 400
    
    def test_login(self):
        """Test user login"""
        # Create user first
        client.post(
            "/api/auth/signup",
            json={"email": "login@example.com", "password": "pass123"}
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "pass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_invalid_password(self):
        """Test login with wrong password"""
        client.post(
            "/api/auth/signup",
            json={"email": "wrong@example.com", "password": "correct"}
        )
        
        response = client.post(
            "/api/auth/login",
            json={"email": "wrong@example.com", "password": "incorrect"}
        )
        assert response.status_code == 401

class TestCostTracking:
    
    def setup_method(self):
        """Setup for each test - create user"""
        resp = client.post(
            "/api/auth/signup",
            json={"email": f"user{id(self)}@example.com", "password": "pass"}
        )
        self.api_key = resp.json()["api_key"]
    
    def test_track_cost(self):
        """Test tracking a cost"""
        response = client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "input_tokens": 1000,
                "output_tokens": 500,
                "metadata": {"feature": "summarization"}
            },
            headers={"Authorization": self.api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["cost"] == 0.06
    
    def test_track_cost_unauthorized(self):
        """Test tracking without auth"""
        response = client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "input_tokens": 1000,
                "output_tokens": 500
            }
        )
        assert response.status_code == 401
    
    def test_get_cost_summary(self):
        """Test getting cost summary"""
        # Track some costs
        for i in range(3):
            client.post(
                "/api/events/track",
                json={
                    "provider": "openai",
                    "model": "gpt-4",
                    "input_tokens": 1000,
                    "output_tokens": 500
                },
                headers={"Authorization": self.api_key}
            )
        
        # Get summary
        response = client.get(
            "/api/costs/summary",
            headers={"Authorization": self.api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_spend"] == 0.18  # 3 * 0.06
        assert "by_provider" in data
        assert "by_model" in data
        assert data["by_provider"]["openai"] == 0.18

class TestBudgetManagement:
    
    def setup_method(self):
        """Setup for each test"""
        resp = client.post(
            "/api/auth/signup",
            json={"email": f"budget{id(self)}@example.com", "password": "pass"}
        )
        self.api_key = resp.json()["api_key"]
    
    def test_set_budget(self):
        """Test setting budget"""
        response = client.post(
            "/api/budgets",
            json={"amount": 1000.0},
            headers={"Authorization": self.api_key}
        )
        assert response.status_code == 200
    
    def test_get_budgets(self):
        """Test getting budget"""
        client.post(
            "/api/budgets",
            json={"amount": 500.0},
            headers={"Authorization": self.api_key}
        )
        
        response = client.get(
            "/api/budgets",
            headers={"Authorization": self.api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["monthly_budget"] == 500.0

class TestRecommendations:
    
    def setup_method(self):
        """Setup for each test"""
        resp = client.post(
            "/api/auth/signup",
            json={"email": f"rec{id(self)}@example.com", "password": "pass"}
        )
        self.api_key = resp.json()["api_key"]
    
    def test_get_recommendations(self):
        """Test getting recommendations"""
        # Track costs
        for i in range(10):
            client.post(
                "/api/events/track",
                json={
                    "provider": "openai",
                    "model": "gpt-4",
                    "input_tokens": 3000,
                    "output_tokens": 1000
                },
                headers={"Authorization": self.api_key}
            )
        
        # Get recommendations
        response = client.get(
            "/api/recommendations",
            headers={"Authorization": self.api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have recommendations for GPT-4 usage
        if data:
            assert "title" in data[0]
            assert "savings_percentage" in data[0]

# ============================================================================
# SMOKE TESTS - Basic Flow
# ============================================================================

class TestSmokeTests:
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()
    
    def test_full_user_flow(self):
        """Test complete user flow"""
        # Signup
        signup = client.post(
            "/api/auth/signup",
            json={"email": "flow@example.com", "password": "test"}
        )
        assert signup.status_code == 200
        api_key = signup.json()["api_key"]
        
        # Set budget
        budget = client.post(
            "/api/budgets",
            json={"amount": 100.0},
            headers={"Authorization": api_key}
        )
        assert budget.status_code == 200
        
        # Track cost
        track = client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "input_tokens": 1000,
                "output_tokens": 200
            },
            headers={"Authorization": api_key}
        )
        assert track.status_code == 200
        
        # Get summary
        summary = client.get(
            "/api/costs/summary",
            headers={"Authorization": api_key}
        )
        assert summary.status_code == 200
        
        # Get recommendations
        recs = client.get(
            "/api/recommendations",
            headers={"Authorization": api_key}
        )
        assert recs.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
