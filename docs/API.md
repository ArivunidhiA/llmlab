# LLMLab API Architecture & Specification

**Version:** 2.0 (Production-Ready)  
**Status:** OpenAPI 3.1 Compliant  
**Base URL:** `https://api.llmlab.io/v1` (or `http://localhost:8000/v1` for local dev)  
**Authentication:** Bearer token (API key)  

---

## TABLE OF CONTENTS

1. API Overview & Design Philosophy
2. Authentication & Security
3. Core API Endpoints
4. Provider Integration Architecture
5. SDK Design (Python/JavaScript)
6. Error Handling & Rate Limiting
7. OpenAPI Specification
8. Extensibility & Plugin System

---

## PART 1: API OVERVIEW & DESIGN PHILOSOPHY

### Core Design Principles

1. **Provider Abstraction** — Unified interface for OpenAI, Anthropic, Azure, Gemini, etc.
2. **REST-First** — Simple HTTP endpoints, no GraphQL (yet)
3. **Streaming-Ready** — Support for SSE (Server-Sent Events) for cost updates
4. **Backward Compatible** — Never break existing endpoints
5. **Self-Documenting** — OpenAPI schema auto-generated from code
6. **Minimal Payload** — Fast responses, explicit fields
7. **Secure by Default** — Encrypted storage, key rotation, audit logs

### API Philosophy: DX First

The API is designed around **Developer Experience**:
- **Boring is better** — REST over gRPC or WebSockets (unless needed)
- **Convention over Configuration** — Sensible defaults for all parameters
- **Progressive Disclosure** — Simple for beginners, powerful for advanced users
- **Fail Fast, Recover Gracefully** — Clear error messages, retry strategies

---

## PART 2: AUTHENTICATION & SECURITY

### API Key Management

#### 1. Generate API Key

```http
POST /v1/auth/api-keys
Authorization: Bearer {auth_token}
Content-Type: application/json

{
  "name": "Production API Key",
  "expires_in_days": 90,
  "permissions": ["read:costs", "read:traces", "write:projects"]
}
```

**Response (201 Created):**
```json
{
  "id": "key_abc123xyz",
  "key": "llmlab_sk_live_abcdef123456...",
  "name": "Production API Key",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-04-15T10:30:00Z",
  "last_used": null,
  "permissions": ["read:costs", "read:traces", "write:projects"]
}
```

**⚠️ IMPORTANT:** Key is only returned once. Store securely in environment variables.

#### 2. List API Keys

```http
GET /v1/auth/api-keys
Authorization: Bearer {auth_token}
```

**Response (200 OK):**
```json
{
  "keys": [
    {
      "id": "key_abc123xyz",
      "name": "Production API Key",
      "created_at": "2024-01-15T10:30:00Z",
      "last_used": "2024-01-16T14:22:10Z",
      "expires_at": "2024-04-15T10:30:00Z",
      "is_active": true
    }
  ],
  "total": 1
}
```

#### 3. Revoke API Key

```http
DELETE /v1/auth/api-keys/{key_id}
Authorization: Bearer {auth_token}
```

**Response (204 No Content)**

### Bearer Token Authentication

All API requests must include the `Authorization` header:

```
Authorization: Bearer llmlab_sk_live_abcdef123456...
```

**Token Format:**
- `llmlab_sk_live_*` = Production key
- `llmlab_sk_test_*` = Test key (rate limited, for development)
- Tokens expire after 30 days (configurable)
- Implement key rotation every 90 days for security

### Encryption at Rest

**Sensitive Fields Encrypted:**
- Provider API keys (AES-256-GCM)
- User passwords (bcrypt, 10 rounds)
- Personal data (PII, if stored)

**Implementation:**
```python
# Backend encryption (FastAPI)
from cryptography.fernet import Fernet

cipher = Fernet(ENCRYPTION_KEY)

# Encrypt on write
encrypted_key = cipher.encrypt(provider_api_key.encode())

# Decrypt on read (in-memory only)
decrypted_key = cipher.decrypt(encrypted_key).decode()
```

---

## PART 3: CORE API ENDPOINTS

### 3.1 Authentication Endpoints

#### POST `/v1/auth/register`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "user_id": "user_xyz789",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "api_key": "llmlab_sk_live_abc123...",
  "plan": "free"
}
```

#### POST `/v1/auth/login`
Login and get API key.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK):**
```json
{
  "api_key": "llmlab_sk_live_xyz...",
  "user_id": "user_xyz789",
  "email": "user@example.com",
  "expires_in": 2592000,
  "refresh_token": "llmlab_refresh_..."
}
```

#### GET `/v1/auth/me`
Get current user profile.

**Response (200 OK):**
```json
{
  "user_id": "user_xyz789",
  "email": "user@example.com",
  "full_name": "John Doe",
  "plan": "pro",
  "plan_expires_at": "2024-02-15T00:00:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "usage": {
    "traces_this_month": 5234,
    "projects": 8,
    "team_members": 3
  }
}
```

#### POST `/v1/auth/logout`
Invalidate current API key.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### 3.2 Projects Endpoints

#### GET `/v1/projects`
List all projects for the authenticated user.

**Query Parameters:**
```
?limit=20&offset=0
?sort_by=name|created_at|spend
?filter=active|archived
```

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": "proj_abc123",
      "name": "Production Chatbot",
      "description": "Customer-facing chatbot for support",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-16T10:00:00Z",
      "owner_id": "user_xyz789",
      "budget": {
        "monthly_limit": 1000.00,
        "current_spend": 245.67,
        "percentage_used": 24.6,
        "alert_threshold": 80
      },
      "providers": ["openai", "anthropic"],
      "stats": {
        "total_api_calls": 42500,
        "total_tokens": 1250000,
        "avg_cost_per_call": 0.0058
      }
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 5
  }
}
```

#### POST `/v1/projects`
Create a new project.

**Request:**
```json
{
  "name": "Agent Research",
  "description": "Experimental agent system for research",
  "budget_monthly": 500.00,
  "alert_threshold": 80,
  "tags": ["research", "experimental"]
}
```

**Response (201 Created):**
```json
{
  "id": "proj_xyz456",
  "name": "Agent Research",
  "description": "Experimental agent system for research",
  "status": "active",
  "created_at": "2024-01-16T10:30:00Z",
  "budget": {
    "monthly_limit": 500.00,
    "current_spend": 0.00,
    "percentage_used": 0
  }
}
```

#### GET `/v1/projects/{project_id}`
Get detailed project information.

**Response (200 OK):**
```json
{
  "id": "proj_abc123",
  "name": "Production Chatbot",
  "description": "Customer-facing chatbot",
  "status": "active",
  "owner_id": "user_xyz789",
  "created_at": "2024-01-01T00:00:00Z",
  "members": [
    {
      "user_id": "user_xyz789",
      "email": "john@example.com",
      "role": "admin",
      "added_at": "2024-01-01T00:00:00Z"
    },
    {
      "user_id": "user_abc123",
      "email": "jane@example.com",
      "role": "member",
      "added_at": "2024-01-10T00:00:00Z"
    }
  ],
  "providers": [
    {
      "id": "prov_123",
      "provider": "openai",
      "name": "OpenAI Production",
      "status": "verified",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    }
  ]
}
```

#### PUT `/v1/projects/{project_id}`
Update project settings.

**Request:**
```json
{
  "name": "Updated Name",
  "budget_monthly": 750.00,
  "alert_threshold": 70,
  "status": "active|archived"
}
```

**Response (200 OK):** Updated project object

#### DELETE `/v1/projects/{project_id}`
Delete a project (cascades to traces, costs).

**Response (204 No Content)**

---

### 3.3 Costs Endpoints

#### GET `/v1/projects/{project_id}/costs`
Get aggregated cost data for a project.

**Query Parameters:**
```
?start_date=2024-01-01&end_date=2024-01-31
?granularity=daily|hourly|total
?group_by=provider|model|day
?include_forecast=true
```

**Response (200 OK):**
```json
{
  "project_id": "proj_abc123",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "summary": {
    "total_cost": 245.67,
    "currency": "USD",
    "average_daily_cost": 7.92,
    "trend": "up_12_percent"
  },
  "breakdown": {
    "by_provider": {
      "openai": {
        "total": 145.23,
        "percentage": 59.1,
        "models": {
          "gpt-4": 89.50,
          "gpt-3.5-turbo": 55.73
        }
      },
      "anthropic": {
        "total": 100.44,
        "percentage": 40.9,
        "models": {
          "claude-3-opus": 100.44
        }
      }
    },
    "by_day": {
      "2024-01-01": 12.34,
      "2024-01-02": 18.92,
      "2024-01-03": 8.45
    }
  },
  "forecast": {
    "end_of_month_projected": 240.50,
    "confidence": 0.87,
    "warning": "At current rate, budget will be 24% exceeded"
  },
  "last_sync": "2024-01-31T23:55:00Z"
}
```

#### GET `/v1/projects/{project_id}/costs/records`
Get detailed cost records (individual API calls).

**Query Parameters:**
```
?provider=openai&model=gpt-4
?start_date=2024-01-15&end_date=2024-01-16
?limit=100&offset=0
?sort_by=cost|timestamp|latency
```

**Response (200 OK):**
```json
{
  "records": [
    {
      "id": "rec_abc123",
      "project_id": "proj_abc123",
      "provider": "openai",
      "model": "gpt-4",
      "timestamp": "2024-01-15T10:30:00Z",
      "cost_usd": 0.12,
      "input_tokens": 500,
      "output_tokens": 100,
      "total_tokens": 600,
      "latency_ms": 1200,
      "api_call_id": "chatcmpl-8xyz123abc",
      "status": "success|error",
      "error_message": null
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 5234
  }
}
```

#### GET `/v1/projects/{project_id}/costs/forecast`
Forecast end-of-month costs based on current burn rate.

**Response (200 OK):**
```json
{
  "project_id": "proj_abc123",
  "current_month_cost": 145.67,
  "days_elapsed": 15,
  "daily_average": 9.71,
  "projected_end_of_month": 291.30,
  "budget_monthly": 1000.00,
  "budget_remaining": 708.70,
  "percentage_of_budget": 29.1,
  "confidence": 0.85,
  "status": "on_track|warning|over_budget",
  "alerts": [
    {
      "type": "budget_overage_warning",
      "message": "If spending continues, you'll exceed budget by $291",
      "recommended_action": "Review model selection or implement cost optimizations"
    }
  ]
}
```

---

### 3.4 Providers Endpoints

#### POST `/v1/projects/{project_id}/providers`
Add a new provider (API key) to a project.

**Request:**
```json
{
  "provider": "openai",
  "name": "OpenAI Production",
  "api_key": "sk-...",
  "organization_id": "org-...",
  "test_connection": true
}
```

**Response (201 Created):**
```json
{
  "id": "prov_abc123",
  "provider": "openai",
  "name": "OpenAI Production",
  "status": "verified",
  "created_at": "2024-01-15T10:30:00Z",
  "last_tested": "2024-01-15T10:30:00Z",
  "models_available": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
  "first_sync": "pending"
}
```

#### GET `/v1/projects/{project_id}/providers`
List all providers for a project.

**Response (200 OK):**
```json
{
  "providers": [
    {
      "id": "prov_abc123",
      "provider": "openai",
      "name": "OpenAI Production",
      "status": "verified|error|unverified",
      "created_at": "2024-01-15T10:30:00Z",
      "last_tested": "2024-01-16T10:00:00Z",
      "last_sync": "2024-01-16T10:00:00Z",
      "models_available": ["gpt-4", "gpt-3.5-turbo"],
      "next_sync": "2024-01-17T10:00:00Z"
    }
  ]
}
```

#### POST `/v1/projects/{project_id}/providers/{provider_id}/test`
Test provider connectivity.

**Response (200 OK):**
```json
{
  "status": "ok|error",
  "message": "Successfully connected to OpenAI",
  "models_available": ["gpt-4", "gpt-3.5-turbo"],
  "last_tested": "2024-01-16T10:30:00Z"
}
```

**Response (400 Bad Request) — If connection fails:**
```json
{
  "status": "error",
  "message": "Invalid API key",
  "code": "invalid_api_key",
  "suggestion": "Check your API key in the dashboard"
}
```

#### POST `/v1/projects/{project_id}/providers/{provider_id}/sync`
Trigger immediate cost sync for a provider.

**Response (202 Accepted):**
```json
{
  "status": "sync_started",
  "provider_id": "prov_abc123",
  "sync_id": "sync_xyz789",
  "estimated_completion": "2024-01-16T10:05:00Z"
}
```

#### DELETE `/v1/projects/{project_id}/providers/{provider_id}`
Remove a provider from a project.

**Response (204 No Content)**

---

### 3.5 Traces Endpoints (Agent Debugging)

#### POST `/v1/projects/{project_id}/traces`
Create a new trace (SDK calls this automatically).

**Request:**
```json
{
  "trace_id": "trace_abc123xyz",
  "agent_name": "customer_support_agent",
  "user_id": "user_123",
  "tags": ["production", "critical"],
  "metadata": {
    "customer_id": "cust_456",
    "conversation_id": "conv_789"
  },
  "steps": [
    {
      "step_id": "step_1",
      "type": "llm_call",
      "model": "gpt-4",
      "provider": "openai",
      "timestamp": "2024-01-15T10:30:00Z",
      "input_tokens": 500,
      "output_tokens": 100,
      "cost": 0.012,
      "latency_ms": 1200,
      "status": "success",
      "prompt": "...",
      "response": "..."
    },
    {
      "step_id": "step_2",
      "type": "tool_call",
      "tool": "search",
      "timestamp": "2024-01-15T10:30:01Z",
      "latency_ms": 500,
      "status": "success",
      "input": "customer order status",
      "output": "Order #123 shipped on Jan 15"
    }
  ],
  "final_status": "success|error|timeout"
}
```

**Response (201 Created):**
```json
{
  "trace_id": "trace_abc123xyz",
  "project_id": "proj_abc123",
  "agent_name": "customer_support_agent",
  "created_at": "2024-01-15T10:30:00Z",
  "total_cost": 0.012,
  "total_latency_ms": 1700,
  "status": "success",
  "step_count": 2
}
```

#### GET `/v1/projects/{project_id}/traces`
List traces for a project.

**Query Parameters:**
```
?agent_name=customer_support_agent
?status=success|error|timeout
?start_date=2024-01-15&end_date=2024-01-16
?min_cost=0.01&max_cost=1.0
?limit=50&offset=0
?sort_by=cost|timestamp|latency
```

**Response (200 OK):**
```json
{
  "traces": [
    {
      "trace_id": "trace_abc123xyz",
      "agent_name": "customer_support_agent",
      "status": "success",
      "created_at": "2024-01-15T10:30:00Z",
      "total_cost": 0.012,
      "total_latency_ms": 1700,
      "step_count": 2,
      "models_used": ["gpt-4"],
      "user_id": "user_123"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1234
  }
}
```

#### GET `/v1/projects/{project_id}/traces/{trace_id}`
Get detailed trace with full execution timeline.

**Response (200 OK):**
```json
{
  "trace_id": "trace_abc123xyz",
  "project_id": "proj_abc123",
  "agent_name": "customer_support_agent",
  "status": "success",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:42Z",
  "total_duration_ms": 102000,
  "total_cost": 0.012,
  "total_tokens": {
    "input": 500,
    "output": 100
  },
  "user_id": "user_123",
  "metadata": {
    "customer_id": "cust_456",
    "conversation_id": "conv_789"
  },
  "timeline": [
    {
      "step_id": "step_1",
      "type": "llm_call",
      "model": "gpt-4",
      "provider": "openai",
      "timestamp": "2024-01-15T10:30:00Z",
      "duration_ms": 1200,
      "cost": 0.012,
      "tokens_in": 500,
      "tokens_out": 100,
      "status": "success",
      "prompt": "You are a customer support agent...",
      "response": "I'll help you with your order..."
    },
    {
      "step_id": "step_2",
      "type": "tool_call",
      "tool": "search_orders",
      "timestamp": "2024-01-15T10:30:01Z",
      "duration_ms": 500,
      "status": "success",
      "input": { "customer_id": "cust_456" },
      "output": { "orders": [...] }
    }
  ]
}
```

#### DELETE `/v1/projects/{project_id}/traces/{trace_id}`
Delete a trace.

**Response (204 No Content)**

---

### 3.6 Alerts Endpoints

#### GET `/v1/projects/{project_id}/alerts`
Get alert configuration and history.

**Response (200 OK):**
```json
{
  "config": {
    "project_id": "proj_abc123",
    "enabled": true,
    "thresholds": [
      {
        "percentage": 50,
        "channels": ["email"]
      },
      {
        "percentage": 75,
        "channels": ["email", "slack"]
      },
      {
        "percentage": 90,
        "channels": ["email", "slack", "pagerduty"]
      }
    ],
    "slack_webhook": "https://hooks.slack.com/services/...",
    "pagerduty_key": "pagerduty_123",
    "notification_email": "team@example.com"
  },
  "recent_alerts": [
    {
      "id": "alert_abc123",
      "threshold": 75,
      "type": "budget_threshold",
      "triggered_at": "2024-01-15T14:00:00Z",
      "current_spend": 750.00,
      "budget_limit": 1000.00,
      "channels_used": ["email", "slack"],
      "status": "sent"
    }
  ]
}
```

#### PUT `/v1/projects/{project_id}/alerts`
Update alert settings.

**Request:**
```json
{
  "enabled": true,
  "thresholds": [50, 75, 90],
  "channels": {
    "email": true,
    "slack": true,
    "pagerduty": false
  },
  "slack_webhook": "https://hooks.slack.com/services/...",
  "notification_email": "team@example.com"
}
```

**Response (200 OK):** Updated alert config

#### POST `/v1/projects/{project_id}/alerts/test`
Send a test alert.

**Request:**
```json
{
  "channel": "email|slack|pagerduty"
}
```

**Response (200 OK):**
```json
{
  "status": "sent",
  "channel": "email",
  "message": "Test alert sent to team@example.com"
}
```

---

### 3.7 Recommendations Endpoints

#### GET `/v1/projects/{project_id}/recommendations`
Get cost optimization recommendations.

**Query Parameters:**
```
?limit=10
?sort_by=potential_savings|confidence|recency
?filter=model_switch|prompt_optimization|caching
?status=new|applied|dismissed
```

**Response (200 OK):**
```json
{
  "project_id": "proj_abc123",
  "total_potential_savings": 450.25,
  "total_confidence": 0.88,
  "recommendations": [
    {
      "id": "rec_abc123",
      "type": "model_switch",
      "priority": "high",
      "created_at": "2024-01-15T10:30:00Z",
      "title": "Switch from GPT-4 to GPT-3.5 Turbo for Summarization",
      "description": "Analysis shows GPT-3.5 Turbo performs equally for summarization tasks",
      "current": {
        "model": "gpt-4",
        "cost_monthly": 450.00
      },
      "recommended": {
        "model": "gpt-3.5-turbo",
        "cost_monthly": 89.50
      },
      "potential_savings": {
        "monthly": 360.50,
        "percentage": 80.1,
        "annual": 4326.00
      },
      "confidence": 0.92,
      "data_points": 1523,
      "reasoning": "Analyzed 1523 API calls. Accuracy parity: 98%",
      "impact_assessment": {
        "accuracy_impact": "negligible (0.2% difference)",
        "latency_impact": "1.2x faster",
        "reliability_impact": "same"
      },
      "estimated_implementation_time": "5 minutes",
      "status": "new|applied|dismissed"
    },
    {
      "id": "rec_abc124",
      "type": "prompt_optimization",
      "priority": "medium",
      "created_at": "2024-01-16T10:00:00Z",
      "title": "Enable Prompt Caching for System Prompts",
      "description": "32% of API calls use identical system prompts",
      "current": {
        "feature": "prompt_caching",
        "status": "disabled",
        "cost_monthly": 450.00
      },
      "recommended": {
        "feature": "prompt_caching",
        "status": "enabled",
        "cost_monthly": 306.00
      },
      "potential_savings": {
        "monthly": 144.00,
        "percentage": 32,
        "annual": 1728.00
      },
      "confidence": 0.87,
      "reasoning": "Detected 487 identical prompts across 1523 calls"
    }
  ]
}
```

#### POST `/v1/projects/{project_id}/recommendations/{rec_id}/apply`
Mark recommendation as applied.

**Response (200 OK):**
```json
{
  "id": "rec_abc123",
  "status": "applied",
  "applied_at": "2024-01-16T10:30:00Z",
  "impact_tracking_started": true
}
```

#### POST `/v1/projects/{project_id}/recommendations/{rec_id}/dismiss`
Dismiss a recommendation.

**Request:**
```json
{
  "reason": "already_implemented|not_applicable|revisit_later",
  "notes": "We're already using GPT-3.5 in some places"
}
```

**Response (200 OK):**
```json
{
  "id": "rec_abc123",
  "status": "dismissed",
  "dismissed_at": "2024-01-16T10:30:00Z"
}
```

---

## PART 4: PROVIDER INTEGRATION ARCHITECTURE

### Provider Plugin Interface

All providers implement a standard interface for maximum extensibility:

```python
# Base provider class (abstract)
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime

class ProviderBase(ABC):
    """Abstract base class for LLM cost providers"""
    
    def __init__(self, api_key: str, credentials: Dict = None):
        self.api_key = api_key
        self.credentials = credentials or {}
    
    @abstractmethod
    async def fetch_costs(self, 
                         start_date: datetime, 
                         end_date: datetime) -> List[CostRecord]:
        """Fetch cost records from provider API"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Test if credentials are valid"""
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """List available models"""
        pass
    
    @abstractmethod
    def get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing for a model
        
        Returns: {
            'input': cost_per_1k_tokens,
            'output': cost_per_1k_tokens
        }
        """
        pass

class CostRecord(BaseModel):
    """Standard cost record format"""
    provider: str
    model: str
    timestamp: datetime
    cost_usd: float
    input_tokens: int
    output_tokens: int
    api_call_id: str
    metadata: Dict = {}
```

### Supported Providers (MVP)

#### 1. OpenAI

```python
class OpenAIProvider(ProviderBase):
    API_BASE = "https://api.openai.com/v1"
    
    async def fetch_costs(self, start_date, end_date):
        """Fetch from OpenAI Billing API"""
        # Requires: organization-level API key with billing access
        # Endpoint: GET /billing/usage
        pass
    
    async def validate_credentials(self):
        """Test with models endpoint"""
        # Endpoint: GET /models
        pass
    
    def get_models(self):
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "text-embedding-ada-002"
        ]
    
    def get_pricing(self, model):
        # Source: https://openai.com/pricing
        pricing = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }
        return pricing.get(model, {})
```

#### 2. Anthropic

```python
class AnthropicProvider(ProviderBase):
    API_BASE = "https://api.anthropic.com/v1"
    
    async def fetch_costs(self, start_date, end_date):
        """Anthropic doesn't expose billing API yet
        
        Workaround:
        1. Users export CSV from console.anthropic.com
        2. Or we store costs from SDK intercepts
        """
        pass
    
    async def validate_credentials(self):
        """Test with messages endpoint"""
        # Make minimal API call to verify key
        pass
    
    def get_models(self):
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def get_pricing(self, model):
        pricing = {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
        }
        return pricing.get(model, {})
```

#### 3. Azure OpenAI

```python
class AzureProvider(ProviderBase):
    """Azure OpenAI Service provider"""
    
    async def fetch_costs(self, start_date, end_date):
        """Fetch from Azure Cost Management API"""
        # Requires: Azure subscription + service principal
        pass
    
    async def validate_credentials(self):
        """Test Azure authentication"""
        pass
    
    def get_models(self):
        # Azure has different deployment names
        return ["gpt-4", "gpt-35-turbo", "text-embedding-ada-002"]
```

#### 4. Google Gemini

```python
class GeminiProvider(ProviderBase):
    """Google Gemini API provider"""
    
    async def fetch_costs(self, start_date, end_date):
        """Fetch from Google Cloud Billing API"""
        # Queries BigQuery table: google.cloud.billing
        pass
    
    def get_models(self):
        return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
```

### Extending to New Providers (Roadmap)

**For developers who want to add a new provider:**

1. **Create new provider class:**
   ```python
   # providers/cohere_provider.py
   from app.providers.base import ProviderBase
   
   class CohereProvider(ProviderBase):
       async def fetch_costs(self, start_date, end_date):
           # Implementation
           pass
       
       # ... other required methods
   ```

2. **Register provider:**
   ```python
   # config/providers.py
   PROVIDERS = {
       "openai": OpenAIProvider,
       "anthropic": AnthropicProvider,
       "cohere": CohereProvider,  # NEW
   }
   ```

3. **Add to UI:**
   ```typescript
   // frontend/components/ProviderSelector.tsx
   const PROVIDER_OPTIONS = [
       { value: "openai", label: "OpenAI" },
       { value: "cohere", label: "Cohere" },  // NEW
   ]
   ```

4. **Test & deploy:**
   ```bash
   pytest tests/test_cohere_provider.py
   ```

---

## PART 5: SDK DESIGN (Python/JavaScript)

### Python SDK

```python
# Install: pip install llmlab

from llmlab import LLMLab, trace

# Initialize
llm = LLMLab(api_key="llmlab_sk_...")

# 1. Auto-trace agent execution
@trace(project="my_project", tags=["production"])
def my_agent(user_query):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_query}]
    )
    return response

# 2. Cost tracking
costs = llm.get_costs(
    project="my_project",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(f"Total: ${costs.total}")

# 3. Get recommendations
recommendations = llm.get_recommendations(project="my_project")
for rec in recommendations:
    print(f"Save ${rec.potential_savings.monthly} by {rec.title}")

# 4. Evaluate models
results = llm.compare_models(
    agent=my_agent,
    models=["gpt-4", "claude-3-opus", "llama-70b"],
    test_cases=[...],
    metric="accuracy"
)
```

### JavaScript SDK

```typescript
// Install: npm install @llmlab/sdk

import { LLMLab, trace } from '@llmlab/sdk';

// Initialize
const llm = new LLMLab({ apiKey: 'llmlab_sk_...' });

// 1. Trace with decorator
@trace({ project: 'my_project', tags: ['production'] })
async function myAgent(userQuery: string) {
    const response = await openai.createChatCompletion({
        model: 'gpt-4',
        messages: [{ role: 'user', content: userQuery }]
    });
    return response;
}

// 2. Get costs
const costs = await llm.getCosts({
    project: 'my_project',
    startDate: '2024-01-01',
    endDate: '2024-01-31'
});
console.log(`Total: $${costs.total}`);

// 3. Stream recommendations
const recommendations = await llm.getRecommendations({ project: 'my_project' });
for (const rec of recommendations) {
    console.log(`Save $${rec.potential_savings.monthly} by ${rec.title}`);
}
```

---

## PART 6: ERROR HANDLING & RATE LIMITING

### Standard Error Response

```json
{
  "status": "error",
  "error": {
    "code": "invalid_request",
    "message": "Invalid API key",
    "details": {
      "field": "api_key",
      "reason": "Key expired or invalid"
    }
  },
  "request_id": "req_abc123xyz",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET request |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Backend error |

### Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705344600
```

**Limits (per 1 hour):**
- Free tier: 100 requests
- Pro tier: 10,000 requests
- Enterprise: Unlimited

### Retry Strategy

```python
# Auto-retry with exponential backoff
import backoff

@backoff.on_exception(
    backoff.expo,
    (ConnectionError, TimeoutError),
    max_tries=3
)
async def fetch_costs():
    return await llm.get_costs(...)
```

---

## PART 7: OPENAPI SPECIFICATION

```yaml
openapi: 3.1.0
info:
  title: LLMLab API
  version: 1.0.0
  description: Cost tracking and optimization for LLM applications
  
servers:
  - url: https://api.llmlab.io/v1
    description: Production
  - url: http://localhost:8000/v1
    description: Local development

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    CostRecord:
      type: object
      properties:
        id:
          type: string
        provider:
          type: string
          enum: [openai, anthropic, azure, gemini]
        model:
          type: string
        cost_usd:
          type: number
        timestamp:
          type: string
          format: date-time
      required: [id, provider, model, cost_usd, timestamp]

    Project:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        budget_monthly:
          type: number
        current_spend:
          type: number

paths:
  /projects:
    get:
      summary: List projects
      security:
        - BearerAuth: []
      responses:
        200:
          description: List of projects
          content:
            application/json:
              schema:
                type: object
                properties:
                  projects:
                    type: array
                    items:
                      $ref: '#/components/schemas/Project'

  /projects/{project_id}/costs:
    get:
      summary: Get project costs
      parameters:
        - name: project_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Cost summary
```

Full OpenAPI spec: `/v1/openapi.json` (auto-generated from code)

---

## PART 8: EXTENSIBILITY & PLUGIN SYSTEM

### Plugin Architecture

LLMLab supports custom plugins for:
1. **New providers** (Cohere, HF, custom APIs)
2. **Custom evals** (domain-specific compliance checks)
3. **Webhooks** (integrations with external systems)

### Creating a Custom Provider Plugin

```python
# my_plugin.py
from llmlab.providers.base import ProviderBase

class MyCustomProvider(ProviderBase):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def fetch_costs(self, start_date, end_date):
        # Fetch from your API
        return [...]
    
    async def validate_credentials(self):
        return True
    
    def get_models(self):
        return ["model1", "model2"]
    
    def get_pricing(self, model):
        return {"input": 0.001, "output": 0.002}

# Register in llmlab
from llmlab.config import register_provider
register_provider("my_provider", MyCustomProvider)

# Use in dashboard
# Dashboard will now show "My Custom Provider" as an option
```

### Webhook System

```python
# Trigger webhooks on events
llm.register_webhook(
    event="cost_alert",
    url="https://your-app.com/webhooks/llmlab",
    secret="webhook_secret_123"
)

# Webhook payload
{
    "event": "cost_alert",
    "project_id": "proj_abc",
    "threshold_reached": 80,
    "current_spend": 800,
    "budget": 1000,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## CONCLUSION

This API is designed for:
- ✅ Developer simplicity
- ✅ Enterprise extensibility
- ✅ Security & compliance
- ✅ Scalability

For implementation details, see the backend codebase. For integrations, see SDK documentation.

**Questions?** See `llmlab/docs/IMPLEMENTATION.md` for backend setup.
