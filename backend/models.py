"""Pydantic models for request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Auth Models
class SignupRequest(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str


class User(BaseModel):
    """User model."""
    id: str
    email: str
    name: str
    created_at: datetime


# Event Tracking Models
class ProviderType(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class EventTrackRequest(BaseModel):
    """Track LLM API call event."""
    provider: ProviderType
    model: str
    input_tokens: int
    output_tokens: int
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class EventResponse(BaseModel):
    """Event tracking response."""
    event_id: str
    user_id: str
    provider: str
    model: str
    total_tokens: int
    cost: float
    tracked_at: datetime


# Cost Summary Models
class CostByModel(BaseModel):
    """Cost breakdown by model."""
    model: str
    provider: str
    total_calls: int
    total_tokens: int
    total_cost: float


class CostByDate(BaseModel):
    """Cost breakdown by date."""
    date: str
    total_cost: float
    call_count: int


class CostSummary(BaseModel):
    """Overall cost summary."""
    total_cost: float
    call_count: int
    average_cost_per_call: float
    by_model: List[CostByModel]
    by_date: List[CostByDate]
    date_range_start: str
    date_range_end: str


# Budget Models
class BudgetStatus(str, Enum):
    """Budget status."""
    OK = "ok"
    WARNING = "warning"
    EXCEEDED = "exceeded"


class Budget(BaseModel):
    """Budget model."""
    id: str
    user_id: str
    limit: float
    period: str  # "monthly", "weekly", "daily"
    current_spend: float
    status: BudgetStatus
    created_at: datetime
    updated_at: datetime
    
    @property
    def percentage_used(self) -> float:
        """Get percentage of budget used."""
        return (self.current_spend / self.limit * 100) if self.limit > 0 else 0
    
    @property
    def remaining(self) -> float:
        """Get remaining budget."""
        return max(0, self.limit - self.current_spend)


class BudgetRequest(BaseModel):
    """Set/update budget request."""
    limit: float = Field(..., gt=0)
    period: str = Field(default="monthly", regex="^(daily|weekly|monthly)$")


class BudgetsResponse(BaseModel):
    """Response with multiple budgets."""
    budgets: List[Budget]
    total_limits: float
    total_spend: float


# Recommendation Models
class CostOptimization(BaseModel):
    """Cost optimization recommendation."""
    type: str
    title: str
    description: str
    potential_savings: float
    priority: str  # "low", "medium", "high"


class Recommendation(BaseModel):
    """Model recommendation."""
    current_model: str
    suggested_model: str
    current_cost_per_call: float
    suggested_cost_per_call: float
    estimated_monthly_savings: float
    use_case: str


class RecommendationsResponse(BaseModel):
    """Recommendations response."""
    optimizations: List[CostOptimization]
    model_recommendations: List[Recommendation]
    anomalies: List[Dict[str, Any]]
    last_updated: datetime


# Health Check Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    database_connected: bool
    timestamp: datetime
