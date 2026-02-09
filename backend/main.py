"""FastAPI application for LLMlab"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from config import settings, get_provider_rates
from database import init_db, get_db
from models import User, Event, Budget, AlertLog
from schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    EventCreate, EventResponse, CostSummary, CostRecommendation,
    BudgetCreate, BudgetResponse, EventSummary, HealthResponse, WebhookUpdate
)
from security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)

# Initialize FastAPI app
app = FastAPI(
    title="LLMlab API",
    description="Cost tracking for LLM APIs",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ STARTUP ============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# ============ HEALTH ============

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")


# ============ AUTH ============

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    access_token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@app.post("/api/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should delete token)"""
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# ============ EVENTS / TRACKING ============

@app.post("/api/events/track", response_model=EventResponse)
async def track_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track an LLM API call event"""
    
    # Calculate cost
    rates = get_provider_rates()
    cost = calculate_cost(
        provider=event_data.provider,
        model=event_data.model,
        input_tokens=event_data.input_tokens,
        output_tokens=event_data.output_tokens,
        rates=rates
    )
    
    # Create event
    event = Event(
        user_id=current_user.id,
        provider=event_data.provider,
        model=event_data.model,
        input_tokens=event_data.input_tokens,
        output_tokens=event_data.output_tokens,
        duration_ms=event_data.duration_ms,
        calculated_cost=cost,
        request_metadata=event_data.request_metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Check budget alerts
    await check_budget_alerts(current_user.id, db)
    
    return event


@app.get("/api/events", response_model=list[EventResponse])
async def list_events(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's tracked events"""
    events = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(Event.created_at.desc()).offset(offset).limit(limit).all()
    
    return events


# ============ COSTS ============

@app.get("/api/costs/summary", response_model=CostSummary)
async def get_costs_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cost summary dashboard"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today.replace(day=1)
    
    # Query events
    all_events = db.query(Event).filter(Event.user_id == current_user.id).all()
    today_events = [e for e in all_events if e.created_at >= today]
    week_events = [e for e in all_events if e.created_at >= week_ago]
    month_events = [e for e in all_events if e.created_at >= month_ago]
    
    # Calculate costs
    today_cost = sum(e.calculated_cost for e in today_events)
    week_cost = sum(e.calculated_cost for e in week_events)
    month_cost = sum(e.calculated_cost for e in month_events)
    total_cost = sum(e.calculated_cost for e in all_events)
    
    # Breakdown by provider
    by_provider = {}
    for event in all_events:
        if event.provider not in by_provider:
            by_provider[event.provider] = 0
        by_provider[event.provider] += event.calculated_cost
    
    # Breakdown by model
    by_model = {}
    for event in all_events:
        if event.model not in by_model:
            by_model[event.model] = 0
        by_model[event.model] += event.calculated_cost
    
    # Breakdown by day (last 30 days)
    by_day = {}
    for event in all_events:
        date_key = event.created_at.strftime("%Y-%m-%d")
        if date_key not in by_day:
            by_day[date_key] = 0
        by_day[date_key] += event.calculated_cost
    
    return CostSummary(
        today=round(today_cost, 4),
        this_week=round(week_cost, 4),
        this_month=round(month_cost, 4),
        total=round(total_cost, 4),
        today_events=len(today_events),
        week_events=len(week_events),
        month_events=len(month_events),
        by_provider=by_provider,
        by_model=by_model,
        by_day=by_day,
    )


@app.get("/api/recommendations", response_model=list[CostRecommendation])
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered cost optimization recommendations"""
    recommendations = []
    
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    if not events:
        return recommendations
    
    # Calculate costs by provider
    costs_by_provider = {}
    for event in events:
        if event.provider not in costs_by_provider:
            costs_by_provider[event.provider] = {"cost": 0, "count": 0}
        costs_by_provider[event.provider]["cost"] += event.calculated_cost
        costs_by_provider[event.provider]["count"] += 1
    
    # Calculate costs by model
    costs_by_model = {}
    for event in events:
        if event.model not in costs_by_model:
            costs_by_model[event.model] = {"cost": 0, "count": 0}
        costs_by_model[event.model]["cost"] += event.calculated_cost
        costs_by_model[event.model]["count"] += 1
    
    # Recommendation: Switch to cheaper models
    if "gpt-4" in costs_by_model and costs_by_model["gpt-4"]["count"] > 10:
        savings = costs_by_model["gpt-4"]["cost"] * 0.7  # 70% savings with gpt-4-turbo
        recommendations.append(CostRecommendation(
            title="Consider GPT-4 Turbo instead of GPT-4",
            description="Your GPT-4 usage is high. GPT-4 Turbo is 3-7x cheaper.",
            potential_savings=round(savings, 2),
            priority="high",
            action="Migrate to gpt-4-turbo-preview"
        ))
    
    # Recommendation: Use cheaper providers
    if "openai" in costs_by_provider and costs_by_provider["openai"]["cost"] > 10:
        recommendations.append(CostRecommendation(
            title="Evaluate Anthropic Claude 3",
            description="Claude 3 Sonnet is 5x cheaper than GPT-4 for most tasks.",
            potential_savings=round(costs_by_provider["openai"]["cost"] * 0.8, 2),
            priority="medium",
            action="Test with claude-3-sonnet"
        ))
    
    # Recommendation: Batch requests
    if len(events) > 100:
        recommendations.append(CostRecommendation(
            title="Implement batch processing",
            description="Batch API calls to reduce per-request overhead.",
            potential_savings=round(sum(e.calculated_cost for e in events) * 0.1, 2),
            priority="medium",
            action="Use batch API endpoints"
        ))
    
    return recommendations


# ============ BUDGETS ============

@app.post("/api/budgets", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new budget"""
    budget = Budget(
        user_id=current_user.id,
        monthly_limit=budget_data.monthly_limit,
        alert_channel=budget_data.alert_channel,
        alert_at_50=budget_data.alert_at_50,
        alert_at_80=budget_data.alert_at_80,
        alert_at_100=budget_data.alert_at_100,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    return format_budget_response(budget, db, current_user.id)


@app.get("/api/budgets", response_model=list[BudgetResponse])
async def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's budgets"""
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return [format_budget_response(b, db, current_user.id) for b in budgets]


@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    for key, value in budget_data.items():
        if value is not None:
            setattr(budget, key, value)
    
    db.commit()
    db.refresh(budget)
    
    return format_budget_response(budget, db, current_user.id)


@app.delete("/api/budgets/{budget_id}")
async def delete_budget(
    budget_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    
    return {"message": "Budget deleted"}


# ============ WEBHOOKS ============

@app.put("/api/webhooks")
async def update_webhooks(
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update webhook URLs"""
    if webhook_data.slack_webhook:
        current_user.slack_webhook = webhook_data.slack_webhook
    if webhook_data.discord_webhook:
        current_user.discord_webhook = webhook_data.discord_webhook
    if webhook_data.email_alerts is not None:
        current_user.email_alerts = webhook_data.email_alerts
    
    db.commit()
    return {"message": "Webhooks updated"}


# ============ HELPERS ============

def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    rates: dict
) -> float:
    """Calculate cost for an event based on tokens and rates"""
    try:
        provider_rates = rates.get(provider, {})
        model_rates = provider_rates.get(model, {})
        
        input_rate = model_rates.get("input", 0)
        output_rate = model_rates.get("output", 0)
        
        input_cost = (input_tokens * input_rate) / 1000
        output_cost = (output_tokens * output_rate) / 1000
        
        return round(input_cost + output_cost, 4)
    except:
        return 0.0


def format_budget_response(budget: Budget, db: Session, user_id: str) -> BudgetResponse:
    """Format budget response with current spend"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_events = db.query(Event).filter(
        Event.user_id == user_id,
        Event.created_at >= month_start
    ).all()
    
    current_spend = sum(e.calculated_cost for e in month_events)
    remaining = max(0, budget.monthly_limit - current_spend)
    percentage_used = min(100, (current_spend / budget.monthly_limit * 100)) if budget.monthly_limit > 0 else 0
    
    return BudgetResponse(
        id=budget.id,
        monthly_limit=budget.monthly_limit,
        alert_channel=budget.alert_channel,
        current_spend=round(current_spend, 2),
        remaining=round(remaining, 2),
        percentage_used=round(percentage_used, 1),
        created_at=budget.created_at,
    )


async def check_budget_alerts(user_id: str, db: Session):
    """Check if budget thresholds are exceeded and send alerts"""
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    
    for budget in budgets:
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_spend = db.query(Event).filter(
            Event.user_id == user_id,
            Event.created_at >= month_start
        ).with_entities(Event.calculated_cost).all()
        
        current_spend = sum(c[0] for c in current_spend)
        percentage = (current_spend / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
        
        # Determine alert type
        alert_type = None
        if budget.alert_at_100 and percentage >= 100:
            alert_type = "100%"
        elif budget.alert_at_80 and 80 <= percentage < 100:
            alert_type = "80%"
        elif budget.alert_at_50 and 50 <= percentage < 80:
            alert_type = "50%"
        
        if alert_type:
            # Log alert
            alert = AlertLog(
                user_id=user_id,
                budget_id=budget.id,
                alert_type=alert_type,
                current_spend=current_spend,
                limit=budget.monthly_limit,
                channel=budget.alert_channel,
            )
            db.add(alert)
            db.commit()
            
            # TODO: Send actual webhook/email notification
            print(f"Alert: User {user_id} at {alert_type} of budget")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
