"""
LLMLab Backend API

A proxy-based LLM cost tracking service.
Users store their real API keys (encrypted), receive proxy keys,
and LLMLab intercepts requests to log usage and costs.

Endpoints:
- POST /auth/github: GitHub OAuth authentication
- POST /api/v1/keys: Store encrypted API key
- GET /api/v1/keys: Get proxy keys
- DELETE /api/v1/keys/{key_id}: Delete an API key
- POST /api/v1/proxy/openai: Proxy OpenAI requests
- POST /api/v1/proxy/anthropic: Proxy Anthropic requests
- GET /api/v1/stats: Get usage statistics
- GET /health: Health check
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_access_token, exchange_github_code, get_current_user
from config import get_settings
from database import get_db, init_db
from models import ApiKey, UsageLog, User
from providers import AnthropicProvider, OpenAIProvider
from schemas import (
    ApiKeyCreate,
    ApiKeyListResponse,
    ApiKeyResponse,
    AuthResponse,
    DailyCost,
    ErrorResponse,
    GitHubAuthRequest,
    HealthResponse,
    ModelCost,
    StatsResponse,
    UserResponse,
)
from security import decrypt_api_key, encrypt_api_key

# =============================================================================
# APP INITIALIZATION
# =============================================================================

# Track server start time
SERVER_START_TIME = time.time()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LLMLab API",
    description="Proxy-based LLM cost tracking service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"success": False, "error": "Rate limit exceeded. Try again later."},
    )


# CORS Middleware
@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_db()


# =============================================================================
# HEALTH CHECK
# =============================================================================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Check API health and database connectivity.

    Returns service status, database connection, and uptime.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    uptime = int(time.time() - SERVER_START_TIME)

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version="1.0.0",
        uptime_seconds=uptime,
    )


# =============================================================================
# AUTHENTICATION
# =============================================================================


@app.post("/auth/github", response_model=AuthResponse, tags=["Authentication"])
async def github_auth(
    request: GitHubAuthRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate via GitHub OAuth.

    Exchange a GitHub OAuth code for a JWT token.
    Creates a new user if first login.

    Args:
        request: Contains GitHub OAuth authorization code.

    Returns:
        AuthResponse: User info and JWT token.
    """
    # Exchange code for GitHub user info
    github_user = await exchange_github_code(request.code)

    # Find or create user
    user = db.query(User).filter(User.github_id == github_user["id"]).first()

    if user is None:
        # Create new user
        user = User(
            github_id=github_user["id"],
            email=github_user["email"],
            username=github_user["username"],
            avatar_url=github_user["avatar_url"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user info
        user.email = github_user["email"]
        user.username = github_user["username"]
        user.avatar_url = github_user["avatar_url"]
        db.commit()

    # Generate JWT token
    token, expires_in = create_access_token(user.id)

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        username=user.username,
        token=token,
        expires_in=expires_in,
    )


@app.get("/api/v1/me", response_model=UserResponse, tags=["Authentication"])
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Get current user's profile.

    Requires authentication.
    """
    return current_user


# =============================================================================
# API KEY MANAGEMENT
# =============================================================================


@app.post("/api/v1/keys", response_model=ApiKeyResponse, tags=["API Keys"])
@limiter.limit("10/minute")
async def create_api_key(
    request: Request,
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiKeyResponse:
    """
    Store an encrypted API key for a provider.

    Your real API key is encrypted and stored securely.
    You receive a proxy key to use in your applications.

    Args:
        key_data: Provider name and your real API key.

    Returns:
        ApiKeyResponse: Proxy key and metadata.
    """
    # Check if user already has a key for this provider
    existing = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == key_data.provider,
        ApiKey.is_active == True,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have an active key for {key_data.provider}. Delete it first to add a new one.",
        )

    # Encrypt the API key
    encrypted = encrypt_api_key(key_data.api_key)

    # Create API key record
    api_key = ApiKey(
        user_id=current_user.id,
        provider=key_data.provider,
        encrypted_key=encrypted,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return ApiKeyResponse(
        id=api_key.id,
        provider=api_key.provider,
        proxy_key=api_key.proxy_key,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        is_active=api_key.is_active,
    )


@app.get("/api/v1/keys", response_model=ApiKeyListResponse, tags=["API Keys"])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiKeyListResponse:
    """
    List all your API keys (proxy keys).

    Returns proxy keys for each provider you've configured.
    Your real API keys are never returned.
    """
    keys = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True,
    ).all()

    return ApiKeyListResponse(
        keys=[
            ApiKeyResponse(
                id=k.id,
                provider=k.provider,
                proxy_key=k.proxy_key,
                created_at=k.created_at,
                last_used_at=k.last_used_at,
                is_active=k.is_active,
            )
            for k in keys
        ]
    )


@app.delete("/api/v1/keys/{key_id}", tags=["API Keys"])
async def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an API key.

    Deactivates the key so it can no longer be used.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id,
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False
    db.commit()

    return {"success": True, "message": "API key deleted"}


# =============================================================================
# PROXY ENDPOINTS
# =============================================================================


async def get_api_key_by_proxy(proxy_key: str, provider: str, db: Session) -> ApiKey:
    """
    Lookup API key by proxy key and provider.

    Args:
        proxy_key: The proxy key from request header.
        provider: Expected provider (openai, anthropic).
        db: Database session.

    Returns:
        ApiKey: The API key record.

    Raises:
        HTTPException: If key not found or invalid.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.proxy_key == proxy_key,
        ApiKey.provider == provider,
        ApiKey.is_active == True,
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or missing proxy key for {provider}",
        )

    return api_key


def extract_proxy_key(request: Request) -> str:
    """
    Extract proxy key from request headers.

    Supports:
    - Authorization: Bearer llmlab_pk_xxx
    - x-api-key: llmlab_pk_xxx
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()

    api_key = request.headers.get("x-api-key", "")
    if api_key:
        return api_key.strip()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing proxy key. Include 'Authorization: Bearer <proxy_key>' header.",
    )


@app.api_route(
    "/api/v1/proxy/openai/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
)
@limiter.limit("100/minute")
async def proxy_openai(
    request: Request,
    path: str,
    db: Session = Depends(get_db),
):
    """
    Proxy requests to OpenAI API.

    Intercepts the request, forwards to OpenAI with your real API key,
    logs token usage and cost, then returns the response unchanged.

    Usage:
    - Set your base URL to: https://llmlab-api.example.com/api/v1/proxy/openai
    - Use your LLMLab proxy key as the API key
    - All requests will be proxied and tracked

    Example:
        ```python
        import openai
        openai.api_base = "https://llmlab-api.example.com/api/v1/proxy/openai"
        openai.api_key = "llmlab_pk_your_proxy_key"
        ```
    """
    # Extract proxy key
    proxy_key = extract_proxy_key(request)

    # Get API key record
    api_key_record = await get_api_key_by_proxy(proxy_key, "openai", db)

    # Decrypt real API key
    real_api_key = decrypt_api_key(api_key_record.encrypted_key)

    # Get request body
    body = await request.body()

    # Parse body to extract model (for cost calculation)
    request_model = "gpt-4o"  # Default
    try:
        body_json = json.loads(body) if body else {}
        request_model = body_json.get("model", request_model)
    except json.JSONDecodeError:
        pass

    # Proxy to OpenAI
    openai_path = f"/v1/{path}"
    headers = dict(request.headers)

    response = await OpenAIProvider.proxy_request(
        api_key=real_api_key,
        path=openai_path,
        method=request.method,
        headers=headers,
        body=body,
    )

    # Parse response for usage tracking
    response_body = response.content
    input_tokens, output_tokens = 0, 0
    actual_model = request_model

    if response.status_code == 200:
        try:
            response_json = response.json()
            input_tokens, output_tokens = OpenAIProvider.extract_usage(response_json)
            actual_model = OpenAIProvider.extract_model(response_json, request_model)
        except Exception:
            pass

    # Calculate cost
    cost = OpenAIProvider.calculate_cost(actual_model, input_tokens, output_tokens)

    # Log usage
    if input_tokens > 0 or output_tokens > 0:
        usage_log = UsageLog(
            user_id=api_key_record.user_id,
            provider="openai",
            model=actual_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        db.add(usage_log)

        # Update last used timestamp
        api_key_record.last_used_at = datetime.utcnow()
        db.commit()

    # Return response with original headers
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers={
            k: v for k, v in response.headers.items()
            if k.lower() not in ("content-encoding", "transfer-encoding", "content-length")
        },
        media_type=response.headers.get("content-type"),
    )


@app.api_route(
    "/api/v1/proxy/anthropic/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
)
@limiter.limit("100/minute")
async def proxy_anthropic(
    request: Request,
    path: str,
    db: Session = Depends(get_db),
):
    """
    Proxy requests to Anthropic API.

    Intercepts the request, forwards to Anthropic with your real API key,
    logs token usage and cost, then returns the response unchanged.

    Usage:
    - Set your base URL to: https://llmlab-api.example.com/api/v1/proxy/anthropic
    - Use your LLMLab proxy key in x-api-key header
    - All requests will be proxied and tracked

    Example:
        ```python
        import anthropic
        client = anthropic.Anthropic(
            base_url="https://llmlab-api.example.com/api/v1/proxy/anthropic",
            api_key="llmlab_pk_your_proxy_key"
        )
        ```
    """
    # Extract proxy key
    proxy_key = extract_proxy_key(request)

    # Get API key record
    api_key_record = await get_api_key_by_proxy(proxy_key, "anthropic", db)

    # Decrypt real API key
    real_api_key = decrypt_api_key(api_key_record.encrypted_key)

    # Get request body
    body = await request.body()

    # Parse body to extract model
    request_model = "claude-3-5-sonnet-20241022"  # Default
    try:
        body_json = json.loads(body) if body else {}
        request_model = body_json.get("model", request_model)
    except json.JSONDecodeError:
        pass

    # Proxy to Anthropic
    anthropic_path = f"/v1/{path}"
    headers = dict(request.headers)

    response = await AnthropicProvider.proxy_request(
        api_key=real_api_key,
        path=anthropic_path,
        method=request.method,
        headers=headers,
        body=body,
    )

    # Parse response for usage tracking
    response_body = response.content
    input_tokens, output_tokens = 0, 0
    actual_model = request_model

    if response.status_code == 200:
        try:
            response_json = response.json()
            input_tokens, output_tokens = AnthropicProvider.extract_usage(response_json)
            actual_model = AnthropicProvider.extract_model(response_json, request_model)
        except Exception:
            pass

    # Calculate cost
    cost = AnthropicProvider.calculate_cost(actual_model, input_tokens, output_tokens)

    # Log usage
    if input_tokens > 0 or output_tokens > 0:
        usage_log = UsageLog(
            user_id=api_key_record.user_id,
            provider="anthropic",
            model=actual_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        db.add(usage_log)

        # Update last used timestamp
        api_key_record.last_used_at = datetime.utcnow()
        db.commit()

    # Return response with original headers
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers={
            k: v for k, v in response.headers.items()
            if k.lower() not in ("content-encoding", "transfer-encoding", "content-length")
        },
        media_type=response.headers.get("content-type"),
    )


# =============================================================================
# STATS ENDPOINT
# =============================================================================


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(
    period: str = Query(
        default="month",
        description="Time period: today, week, month, or all",
        pattern="^(today|week|month|all)$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    """
    Get usage statistics and costs.

    Args:
        period: Time period to query (today, week, month, all).

    Returns:
        StatsResponse: Total costs, breakdown by model and by day.
    """
    now = datetime.utcnow()

    # Calculate date range
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:  # all
        start_date = datetime(2000, 1, 1)  # Effectively all time

    # Query usage logs
    query = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id,
        UsageLog.created_at >= start_date,
    )

    logs = query.all()

    # Calculate totals
    total_usd = sum(log.cost_usd for log in logs)
    total_calls = len(logs)
    total_tokens = sum(log.input_tokens + log.output_tokens for log in logs)

    # Group by model
    model_stats = {}
    for log in logs:
        key = (log.model, log.provider)
        if key not in model_stats:
            model_stats[key] = {
                "model": log.model,
                "provider": log.provider,
                "total_tokens": 0,
                "cost_usd": 0.0,
                "call_count": 0,
            }
        model_stats[key]["total_tokens"] += log.input_tokens + log.output_tokens
        model_stats[key]["cost_usd"] += log.cost_usd
        model_stats[key]["call_count"] += 1

    by_model = [
        ModelCost(
            model=v["model"],
            provider=v["provider"],
            total_tokens=v["total_tokens"],
            cost_usd=round(v["cost_usd"], 6),
            call_count=v["call_count"],
        )
        for v in sorted(model_stats.values(), key=lambda x: x["cost_usd"], reverse=True)
    ]

    # Group by day
    day_stats = {}
    for log in logs:
        date_key = log.created_at.strftime("%Y-%m-%d")
        if date_key not in day_stats:
            day_stats[date_key] = {"cost_usd": 0.0, "call_count": 0}
        day_stats[date_key]["cost_usd"] += log.cost_usd
        day_stats[date_key]["call_count"] += 1

    by_day = [
        DailyCost(
            date=k,
            cost_usd=round(v["cost_usd"], 6),
            call_count=v["call_count"],
        )
        for k, v in sorted(day_stats.items())
    ]

    return StatsResponse(
        period=period,
        total_usd=round(total_usd, 6),
        total_calls=total_calls,
        total_tokens=total_tokens,
        by_model=by_model,
        by_day=by_day,
    )


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
