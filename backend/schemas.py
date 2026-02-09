"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ AUTH ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============ EVENTS ============

class EventCreate(BaseModel):
    provider: str  # openai, anthropic, google, cohere
    model: str  # gpt-4, claude-3, etc
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0
    request_metadata: Optional[dict] = {}


class EventResponse(BaseModel):
    id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: float
    calculated_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventSummary(BaseModel):
    total_events: int
    total_cost: float
    total_tokens: int
    providers: dict  # {provider: {count, cost}}
    models: dict  # {model: {count, cost}}
    by_day: dict  # {date: {count, cost}}


# ============ COSTS ============

class CostSummary(BaseModel):
    today: float = 0.0
    this_week: float = 0.0
    this_month: float = 0.0
    total: float = 0.0
    
    today_events: int = 0
    week_events: int = 0
    month_events: int = 0
    
    by_provider: dict  # {provider: cost}
    by_model: dict  # {model: cost}
    by_day: dict  # {date: cost}


class CostRecommendation(BaseModel):
    title: str
    description: str
    potential_savings: float
    priority: str  # high, medium, low
    action: str


# ============ BUDGETS ============

class BudgetCreate(BaseModel):
    monthly_limit: float
    alert_channel: str = "email"  # email, slack, discord
    alert_at_50: bool = True
    alert_at_80: bool = True
    alert_at_100: bool = True


class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = None
    alert_channel: Optional[str] = None
    alert_at_50: Optional[bool] = None
    alert_at_80: Optional[bool] = None
    alert_at_100: Optional[bool] = None


class BudgetResponse(BaseModel):
    id: str
    monthly_limit: float
    alert_channel: str
    current_spend: float
    remaining: float
    percentage_used: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class BudgetAlert(BaseModel):
    budget_id: str
    current_spend: float
    limit: float
    percentage: int
    alert_type: str  # 50%, 80%, 100%


# ============ WEBHOOKS ============

class WebhookUpdate(BaseModel):
    slack_webhook: Optional[str] = None
    discord_webhook: Optional[str] = None
    email_alerts: Optional[bool] = None


# ============ API KEYS ============

class APIKeyCreate(BaseModel):
    provider: str
    encrypted_key: str


class APIKeyResponse(BaseModel):
    id: str
    provider: str
    key_prefix: str
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


# ============ HEALTH ============

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    database: str = "connected"
    timestamp: datetime
