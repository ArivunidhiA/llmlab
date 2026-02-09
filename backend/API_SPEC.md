# LLMLab API Specification

## Base URL
```
http://localhost:8000
```

## Authentication

All endpoints except `/api/health`, `/api/auth/signup`, and `/api/auth/login` require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### AUTH ENDPOINTS

#### POST `/api/auth/signup`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors:**
- `400` - Email already registered
- `422` - Validation error (password < 8 chars)

---

#### POST `/api/auth/login`
Authenticate user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors:**
- `401` - Invalid email or password

---

#### POST `/api/auth/logout`
Logout user (client-side token removal).

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### EVENT TRACKING ENDPOINTS

#### POST `/api/events/track`
Track an LLM API call.

**Request:**
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "input_tokens": 1000,
  "output_tokens": 500,
  "cost": null,
  "metadata": {
    "conversation_id": "conv_123",
    "session": "prod"
  },
  "timestamp": "2024-02-09T12:00:00Z"
}
```

**Response (201):**
```json
{
  "event_id": "evt_123",
  "user_id": "usr_456",
  "provider": "openai",
  "model": "gpt-4",
  "total_tokens": 1500,
  "cost": 0.045,
  "tracked_at": "2024-02-09T12:00:00Z"
}
```

**Providers:**
- `openai` - OpenAI API
- `anthropic` - Anthropic Claude API
- `google` - Google Gemini API

**Errors:**
- `400` - Validation error
- `401` - Unauthorized

---

#### GET `/api/events/`
List user's tracked events.

**Query Parameters:**
- None

**Response (200):**
```json
{
  "count": 42,
  "events": [
    {
      "event_id": "evt_123",
      "user_id": "usr_456",
      "provider": "openai",
      "model": "gpt-4",
      "input_tokens": 1000,
      "output_tokens": 500,
      "total_tokens": 1500,
      "cost": 0.045,
      "timestamp": "2024-02-09T12:00:00Z"
    }
  ]
}
```

---

### COST ANALYTICS ENDPOINTS

#### GET `/api/costs/summary`
Get cost summary for time period.

**Query Parameters:**
- `days` (int, 1-365, default: 30) - Days to include in summary

**Response (200):**
```json
{
  "total_cost": 125.45,
  "call_count": 250,
  "average_cost_per_call": 0.5018,
  "by_model": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "total_calls": 50,
      "total_tokens": 75000,
      "total_cost": 75.50
    }
  ],
  "by_date": [
    {
      "date": "2024-02-09",
      "total_cost": 12.35,
      "call_count": 25
    }
  ],
  "date_range_start": "2024-01-10",
  "date_range_end": "2024-02-09"
}
```

---

#### GET `/api/costs/by-provider`
Get costs broken down by provider.

**Query Parameters:**
- `days` (int, 1-365, default: 30) - Days to include

**Response (200):**
```json
{
  "date_range": {
    "start": "2024-01-10",
    "end": "2024-02-09"
  },
  "provider_costs": [
    {
      "provider": "openai",
      "total_cost": 85.20,
      "call_count": 200,
      "models": {
        "gpt-4": {
          "cost": 60.50,
          "calls": 100
        },
        "gpt-3.5-turbo": {
          "cost": 24.70,
          "calls": 100
        }
      }
    }
  ]
}
```

---

#### GET `/api/costs/top-models`
Get most expensive models.

**Query Parameters:**
- `limit` (int, 1-100, default: 10) - Number of models to return
- `days` (int, 1-365, default: 30) - Days to include

**Response (200):**
```json
{
  "count": 5,
  "models": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "total_calls": 100,
      "total_tokens": 150000,
      "total_cost": 75.50
    }
  ]
}
```

---

### BUDGET ENDPOINTS

#### GET `/api/budgets`
Get user's budgets.

**Response (200):**
```json
{
  "budgets": [
    {
      "id": "bdg_123",
      "user_id": "usr_456",
      "limit": 100.0,
      "period": "monthly",
      "current_spend": 45.67,
      "status": "ok",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-02-09T12:00:00Z"
    }
  ],
  "total_limits": 300.0,
  "total_spend": 89.34
}
```

**Budget Status:**
- `ok` - Under 80% of limit
- `warning` - 80-100% of limit
- `exceeded` - Over 100% of limit

---

#### POST `/api/budgets`
Create or update a budget.

**Request:**
```json
{
  "limit": 100.0,
  "period": "monthly"
}
```

**Periods:**
- `daily` - Daily budget
- `weekly` - Weekly budget
- `monthly` - Monthly budget

**Response (201):**
```json
{
  "id": "bdg_123",
  "user_id": "usr_456",
  "limit": 100.0,
  "period": "monthly",
  "current_spend": 0.0,
  "status": "ok",
  "created_at": "2024-02-09T12:00:00Z",
  "updated_at": "2024-02-09T12:00:00Z"
}
```

**Errors:**
- `400` - Invalid limit or period

---

#### DELETE `/api/budgets/{budget_id}`
Delete a budget.

**Response (204):** No content

**Errors:**
- `404` - Budget not found
- `403` - Not authorized

---

### RECOMMENDATIONS ENDPOINTS

#### GET `/api/recommendations`
Get all recommendations.

**Query Parameters:**
- `days` (int, 1-365, default: 30) - Days to analyze

**Response (200):**
```json
{
  "optimizations": [
    {
      "type": "batch_processing",
      "title": "Implement Batch Processing",
      "description": "Group multiple requests...",
      "potential_savings": 25.50,
      "priority": "high"
    }
  ],
  "model_recommendations": [
    {
      "current_model": "gpt-4",
      "suggested_model": "gpt-4-turbo",
      "current_cost_per_call": 0.09,
      "suggested_cost_per_call": 0.04,
      "estimated_monthly_savings": 500.00,
      "use_case": "Complex reasoning"
    }
  ],
  "anomalies": [
    {
      "event_id": "evt_999",
      "model": "gpt-4",
      "cost": 5.50,
      "z_score": 3.2,
      "severity": "high"
    }
  ],
  "last_updated": "2024-02-09T12:00:00Z"
}
```

---

#### GET `/api/recommendations/anomalies`
Detect spending anomalies.

**Query Parameters:**
- `days` (int, 1-365, default: 30) - Days to analyze
- `threshold` (float, 1.0-5.0, default: 2.0) - Z-score threshold

**Response (200):**
```json
{
  "count": 3,
  "anomalies": [
    {
      "event_id": "evt_999",
      "model": "gpt-4",
      "cost": 5.50,
      "z_score": 3.2,
      "severity": "high"
    }
  ],
  "analysis_period": {
    "start": "2024-01-10",
    "end": "2024-02-09"
  }
}
```

---

#### GET `/api/recommendations/model-switching`
Get model switching recommendations.

**Query Parameters:**
- `days` (int, 1-365, default: 30) - Days to analyze

**Response (200):**
```json
{
  "count": 2,
  "recommendations": [
    {
      "current_model": "gpt-4",
      "suggested_model": "gpt-4-turbo",
      "current_cost_per_call": 0.09,
      "suggested_cost_per_call": 0.04,
      "estimated_monthly_savings": 500.00,
      "use_case": "Complex reasoning"
    }
  ],
  "total_potential_savings": 750.00
}
```

---

### HEALTH ENDPOINT

#### GET `/api/health`
Health check.

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "database_connected": true,
  "timestamp": "2024-02-09T12:00:00Z"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

### Common Status Codes
- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting. Recommended to add:
- 100 requests/minute per user
- 1000 requests/hour per user

---

## Pagination

Cost summary and event listing support:
- `limit` - Results per page
- `offset` - Start position

---

## Timestamps

All timestamps are in ISO 8601 format (UTC):
```
2024-02-09T12:00:00Z
```

---

## Data Types

### Cost Values
All cost values are in USD and stored with 6 decimal places precision.

### Token Counts
Token counts are integers (whole tokens).

### Percentages
Percentages are floats (0-100).
