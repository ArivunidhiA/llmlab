"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime
import json

client = TestClient(app)


class TestHealthEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "uptime_seconds" in data
        assert "database_connected" in data


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_signup_success(self):
        """Test successful signup."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
    
    def test_signup_duplicate_email(self):
        """Test signup with duplicate email."""
        # First signup
        client.post(
            "/api/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "name": "User One",
            }
        )
        
        # Second signup with same email
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "password456",
                "name": "User Two",
            }
        )
        
        assert response.status_code == 400
    
    def test_signup_short_password(self):
        """Test signup with short password."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short",
                "name": "Test User",
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self):
        """Test successful login."""
        # Create user
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "email": "login@example.com",
                "password": "password123",
                "name": "Login User",
            }
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        # Create user
        client.post(
            "/api/auth/signup",
            json={
                "email": "wrong-pass@example.com",
                "password": "correctpassword",
                "name": "User",
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "wrong-pass@example.com",
                "password": "wrongpassword",
            }
        )
        
        assert response.status_code == 401
    
    def test_logout(self):
        """Test logout endpoint."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestEventTrackingEndpoint:
    """Test suite for event tracking endpoint."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "events@example.com",
                "password": "password123",
                "name": "Events User",
            }
        )
        return response.json()["access_token"]
    
    def test_track_event_success(self, auth_token):
        """Test successful event tracking."""
        response = client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "input_tokens": 100,
                "output_tokens": 50,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "event_id" in data
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4"
        assert data["total_tokens"] == 150
        assert "cost" in data
    
    def test_track_event_custom_cost(self, auth_token):
        """Test event tracking with custom cost."""
        response = client.post(
            "/api/events/track",
            json={
                "provider": "anthropic",
                "model": "claude-3-opus",
                "input_tokens": 500,
                "output_tokens": 300,
                "cost": 0.015,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["cost"] == 0.015
    
    def test_track_event_without_auth(self):
        """Test event tracking without authentication."""
        response = client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "input_tokens": 100,
                "output_tokens": 50,
            }
        )
        
        assert response.status_code == 401
    
    def test_list_events(self, auth_token):
        """Test listing events."""
        # Track an event first
        client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "input_tokens": 100,
                "output_tokens": 50,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # List events
        response = client.get(
            "/api/events/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "events" in data
        assert data["count"] >= 1


class TestCostsEndpoint:
    """Test suite for cost reporting endpoints."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "costs@example.com",
                "password": "password123",
                "name": "Costs User",
            }
        )
        return response.json()["access_token"]
    
    def test_cost_summary(self, auth_token):
        """Test getting cost summary."""
        # Track some events
        for i in range(3):
            client.post(
                "/api/events/track",
                json={
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "input_tokens": 100 * (i + 1),
                    "output_tokens": 50 * (i + 1),
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Get summary
        response = client.get(
            "/api/costs/summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data
        assert "call_count" in data
        assert data["call_count"] >= 3
        assert "by_model" in data
        assert "by_date" in data
    
    def test_costs_by_provider(self, auth_token):
        """Test getting costs by provider."""
        # Track events from different providers
        client.post(
            "/api/events/track",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "input_tokens": 100,
                "output_tokens": 50,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        client.post(
            "/api/events/track",
            json={
                "provider": "anthropic",
                "model": "claude-3-opus",
                "input_tokens": 100,
                "output_tokens": 50,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get breakdown by provider
        response = client.get(
            "/api/costs/by-provider",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "provider_costs" in data
        assert len(data["provider_costs"]) >= 2
    
    def test_top_models(self, auth_token):
        """Test getting top models by cost."""
        response = client.get(
            "/api/costs/top-models?limit=5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "models" in data


class TestBudgetsEndpoint:
    """Test suite for budget management endpoints."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "budgets@example.com",
                "password": "password123",
                "name": "Budgets User",
            }
        )
        return response.json()["access_token"]
    
    def test_create_budget(self, auth_token):
        """Test creating a budget."""
        response = client.post(
            "/api/budgets",
            json={
                "limit": 100.0,
                "period": "monthly",
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["limit"] == 100.0
        assert data["period"] == "monthly"
        assert data["status"] in ["ok", "warning", "exceeded"]
    
    def test_get_budgets(self, auth_token):
        """Test getting all budgets."""
        # Create a budget
        client.post(
            "/api/budgets",
            json={
                "limit": 50.0,
                "period": "weekly",
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get budgets
        response = client.get(
            "/api/budgets",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "budgets" in data
        assert "total_limits" in data
        assert "total_spend" in data
    
    def test_delete_budget(self, auth_token):
        """Test deleting a budget."""
        # Create a budget
        create_response = client.post(
            "/api/budgets",
            json={
                "limit": 75.0,
                "period": "daily",
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        budget_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(
            f"/api/budgets/{budget_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204


class TestRecommendationsEndpoint:
    """Test suite for recommendations endpoint."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "recommendations@example.com",
                "password": "password123",
                "name": "Recommendations User",
            }
        )
        return response.json()["access_token"]
    
    def test_get_recommendations(self, auth_token):
        """Test getting recommendations."""
        response = client.get(
            "/api/recommendations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "optimizations" in data
        assert "model_recommendations" in data
        assert "anomalies" in data
    
    def test_detect_anomalies(self, auth_token):
        """Test anomaly detection."""
        response = client.get(
            "/api/recommendations/anomalies",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "anomalies" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
