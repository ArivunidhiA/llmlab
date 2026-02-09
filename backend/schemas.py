"""
Pydantic schemas for request/response validation.

All API inputs and outputs are validated through these schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# AUTHENTICATION
# =============================================================================


class GitHubAuthRequest(BaseModel):
    """Request to exchange GitHub OAuth code for token."""

    code: str = Field(..., description="GitHub OAuth authorization code")


class AuthResponse(BaseModel):
    """Response after successful authentication."""

    user_id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    username: Optional[str] = Field(None, description="GitHub username")
    token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Token expiry in seconds")


class UserResponse(BaseModel):
    """User profile information."""

    id: str
    github_id: int
    email: str
    username: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# API KEYS
# =============================================================================


class ApiKeyCreate(BaseModel):
    """Request to store a new API key."""

    provider: str = Field(
        ...,
        description="Provider name",
        pattern="^(openai|anthropic)$",
    )
    api_key: str = Field(
        ...,
        min_length=10,
        description="Your real API key for the provider",
    )


class ApiKeyResponse(BaseModel):
    """Response after creating/retrieving API key."""

    id: str = Field(..., description="Key identifier")
    provider: str = Field(..., description="Provider name")
    proxy_key: str = Field(..., description="Proxy key to use in your apps")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    is_active: bool = Field(..., description="Whether key is active")

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    """List of user's API keys."""

    keys: List[ApiKeyResponse]


# =============================================================================
# PROXY
# =============================================================================


class ProxyResponse(BaseModel):
    """Generic proxy response wrapper."""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# =============================================================================
# STATS
# =============================================================================


class ModelCost(BaseModel):
    """Cost breakdown for a single model."""

    model: str = Field(..., description="Model name")
    provider: str = Field(..., description="Provider name")
    total_tokens: int = Field(..., description="Total tokens used")
    cost_usd: float = Field(..., description="Total cost in USD")
    call_count: int = Field(..., description="Number of API calls")


class DailyCost(BaseModel):
    """Cost for a single day."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    cost_usd: float = Field(..., description="Total cost for the day")
    call_count: int = Field(..., description="Number of API calls")


class StatsResponse(BaseModel):
    """User's cost statistics."""

    period: str = Field(..., description="Time period (today, week, month, all)")
    total_usd: float = Field(..., description="Total cost in USD")
    total_calls: int = Field(..., description="Total number of API calls")
    total_tokens: int = Field(..., description="Total tokens used")
    by_model: List[ModelCost] = Field(..., description="Cost breakdown by model")
    by_day: List[DailyCost] = Field(..., description="Cost breakdown by day")


# =============================================================================
# HEALTH
# =============================================================================


class HealthResponse(BaseModel):
    """API health check response."""

    status: str = Field(default="healthy", description="Service status")
    database: str = Field(..., description="Database connection status")
    version: str = Field(default="1.0.0", description="API version")
    uptime_seconds: int = Field(..., description="Server uptime in seconds")


# =============================================================================
# ERROR RESPONSES
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
