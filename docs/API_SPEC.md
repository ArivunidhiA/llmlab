# LLMLab API Specification

## Overview

All endpoints return JSON with consistent format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Base URL**: `https://llmlab-backend.up.railway.app` (or localhost:8000 for dev)

**Authentication**: JWT token in `Authorization: Bearer {token}` header

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure-password-123"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "api_key": "llmlab_sk_12345678901234567890",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_expires_in": 86400
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 400: Email already exists
- 400: Password too weak

---

### POST /api/auth/login

Login to existing account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure-password-123"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_expires_in": 86400,
    "api_key": "llmlab_sk_12345678901234567890"
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 401: Invalid email or password
- 404: User not found

---

## Cost Tracking Endpoints

### POST /api/events/track

Log an LLM API call.

**Request**:
```json
{
  "model": "gpt-4",
  "provider": "openai",
  "tokens_input": 500,
  "tokens_output": 200,
  "timestamp": "2024-02-09T10:00:00Z",
  "metadata": {
    "endpoint": "/api/v1/chat/completions",
    "status_code": 200
  }
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "event_id": "550e8400-e29b-41d4-a716-446655440001",
    "model": "gpt-4",
    "provider": "openai",
    "cost_usd": 0.0175,
    "tokens_input": 500,
    "tokens_output": 200,
    "timestamp": "2024-02-09T10:00:00Z"
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 400: Invalid model or provider
- 401: Unauthorized (invalid token)
- 429: Rate limit exceeded (>100 requests/min)

---

### GET /api/costs/summary

Get cost dashboard data (total, by model, trends).

**Query Parameters**:
- `period`: "day" | "week" | "month" | "all" (default: "month")

**Request**:
```
GET /api/costs/summary?period=month
Authorization: Bearer {token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_usd": 1234.56,
    "period": "month",
    "by_model": [
      {
        "model": "gpt-4",
        "provider": "openai",
        "cost_usd": 500.00,
        "call_count": 100
      },
      {
        "model": "claude-3-opus",
        "provider": "anthropic",
        "cost_usd": 400.00,
        "call_count": 80
      },
      {
        "model": "gemini-pro",
        "provider": "google",
        "cost_usd": 334.56,
        "call_count": 500
      }
    ],
    "by_provider": [
      {
        "provider": "openai",
        "cost_usd": 500.00
      },
      {
        "provider": "anthropic",
        "cost_usd": 400.00
      },
      {
        "provider": "google",
        "cost_usd": 334.56
      }
    ],
    "daily_costs": [
      {
        "date": "2024-02-01",
        "cost_usd": 40.00
      },
      {
        "date": "2024-02-02",
        "cost_usd": 45.00
      }
      // ... 27 more days
    ]
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 400: Invalid period

---

## Budget Management Endpoints

### GET /api/budgets

Get user's budget and usage.

**Request**:
```
GET /api/budgets
Authorization: Bearer {token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "budget_id": "550e8400-e29b-41d4-a716-446655440002",
    "amount_usd": 1000.00,
    "period": "monthly",
    "spent_usd": 1234.56,
    "percentage_used": 123.5,
    "remaining_usd": -234.56,
    "alert_80_percent": true,
    "alert_100_percent": true,
    "reset_date": "2024-03-01"
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 404: Budget not found

---

### POST /api/budgets

Create or update budget.

**Request**:
```json
{
  "amount_usd": 2000.00,
  "period": "monthly"
}
```

**Response** (201 or 200):
```json
{
  "success": true,
  "data": {
    "budget_id": "550e8400-e29b-41d4-a716-446655440002",
    "amount_usd": 2000.00,
    "period": "monthly",
    "created_at": "2024-02-09T10:00:00Z"
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 400: Invalid amount or period
- 401: Unauthorized

---

## Recommendations Endpoint

### GET /api/recommendations

Get cost-saving recommendations.

**Request**:
```
GET /api/recommendations
Authorization: Bearer {token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "rec_001",
        "type": "model_switch",
        "title": "Switch to GPT-3.5-turbo",
        "description": "You're using GPT-4 for 80% of calls. GPT-3.5-turbo is 10x cheaper and handles 95% of your use cases.",
        "current_model": "gpt-4",
        "suggested_model": "gpt-3.5-turbo",
        "current_cost_usd": 500.00,
        "suggested_cost_usd": 50.00,
        "potential_savings_usd": 450.00,
        "potential_savings_percent": 90,
        "confidence": 0.95,
        "effort": "low"
      },
      {
        "id": "rec_002",
        "type": "provider_switch",
        "title": "Consider Claude 2.1 for long document analysis",
        "description": "Claude 2.1 has 200K context window and costs 50% less than GPT-4 for your document analysis tasks.",
        "current_provider": "openai",
        "suggested_provider": "anthropic",
        "potential_savings_usd": 150.00,
        "confidence": 0.85,
        "effort": "medium"
      }
    ],
    "total_potential_savings_usd": 600.00
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**Errors**:
- 401: Unauthorized
- 400: Insufficient data for recommendations (need >10 cost events)

---

## Health Endpoint

### GET /health

Check API uptime.

**Request**:
```
GET /health
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime_seconds": 123456,
    "database": "connected",
    "version": "0.1.0"
  },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "data": null,
  "error": "Error message describing what went wrong",
  "timestamp": "2024-02-09T10:00:00Z"
}
```

**HTTP Status Codes**:
- 200: Success
- 201: Created
- 400: Bad request (validation error)
- 401: Unauthorized (invalid token)
- 404: Not found
- 429: Rate limit exceeded
- 500: Server error

---

## Rate Limiting

- **Global**: 100 requests/minute per API key
- **Burst**: 10 requests/second
- Headers returned with every response:
  - `X-RateLimit-Limit: 100`
  - `X-RateLimit-Remaining: 85`
  - `X-RateLimit-Reset: 1707470000` (Unix timestamp)

---

## Authentication Flow

1. **Signup** → GET `api_key` and `token`
2. **Store** `api_key` in `~/.llmlab/config.json`
3. **Send** `Authorization: Bearer {token}` on all requests
4. **Token expires** in 24 hours → re-login to get new token
5. **API key never expires** → can use to auto-login

---

## Example Usage

### cURL

```bash
# Signup
curl -X POST https://llmlab-backend.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password"
  }'

# Track event
curl -X POST https://llmlab-backend.up.railway.app/api/events/track \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "provider": "openai",
    "tokens_input": 500,
    "tokens_output": 200
  }'

# Get summary
curl https://llmlab-backend.up.railway.app/api/costs/summary?period=month \
  -H "Authorization: Bearer {token}"
```

### Python

```python
import requests

# Signup
response = requests.post(
    "https://llmlab-backend.up.railway.app/api/auth/signup",
    json={
        "email": "user@example.com",
        "password": "secure-password"
    }
)
token = response.json()["data"]["token"]

# Track event
requests.post(
    "https://llmlab-backend.up.railway.app/api/events/track",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model": "gpt-4",
        "provider": "openai",
        "tokens_input": 500,
        "tokens_output": 200
    }
)

# Get summary
response = requests.get(
    "https://llmlab-backend.up.railway.app/api/costs/summary",
    headers={"Authorization": f"Bearer {token}"},
    params={"period": "month"}
)
print(response.json())
```

---

This API is designed to be **simple**, **intuitive**, and **easy to integrate** with any Python, JavaScript, or web application.
