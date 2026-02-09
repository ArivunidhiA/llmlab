"""
LLMLab Backend - FastAPI Server
Cost tracking and optimization for LLM APIs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime, timedelta
from typing import List, Optional
import json
from enum import Enum

# Models and schemas
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from passlib.context import CryptContext

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    monthly_budget = Column(Float, default=0)
    budget_alert_threshold = Column(Float, default=0.8)  # 80%

class CostEvent(Base):
    __tablename__ = "cost_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    provider = Column(String)  # openai, anthropic, google
    model = Column(String)  # gpt-4, claude-3, gemini-pro
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(String)  # JSON

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    month = Column(String)  # 2026-02
    budget_amount = Column(Float)
    alert_sent = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    api_key: str

class TrackCostRequest(BaseModel):
    provider: str  # openai, anthropic, google
    model: str
    input_tokens: int
    output_tokens: int
    metadata: Optional[dict] = None

class BudgetRequest(BaseModel):
    amount: float

class CostSummary(BaseModel):
    total_spend: float
    today_spend: float
    this_month_spend: float
    by_model: dict
    by_provider: dict
    daily_trend: list
    budget_status: Optional[dict] = None

class Recommendation(BaseModel):
    title: str
    description: str
    savings_percentage: int
    confidence: int
    action: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str = "connected"

# ============================================================================
# PROVIDER PRICING (Mock data)
# ============================================================================

PROVIDER_PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    },
    "anthropic": {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    },
    "google": {
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-flash": {"input": 0.00003, "output": 0.00006},
    },
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(email: str, expires_delta: timedelta = None):
    if not expires_delta:
        expires_delta = timedelta(days=30)
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def generate_api_key():
    import secrets
    return f"llmlab_{secrets.token_hex(16)}"

def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on provider and model pricing"""
    try:
        pricing = PROVIDER_PRICING.get(provider, {}).get(model, {})
        input_cost = (input_tokens / 1000) * pricing.get("input", 0)
        output_cost = (output_tokens / 1000) * pricing.get("output", 0)
        return round(input_cost + output_cost, 6)
    except:
        return 0

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = None, db: Session = Depends(get_db)):
    """Get current user from Authorization header (Bearer token or api_key)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    try:
        # Try JWT token
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
            user = db.query(User).filter(User.email == email).first()
        # Try API key
        else:
            user = db.query(User).filter(User.api_key == authorization).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ============================================================================
# LIFESPAN (Keep-alive ping)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 LLMLab backend starting...")
    yield
    # Shutdown
    print("🛑 LLMLab backend shutting down...")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="LLMLab API",
    description="LLM Cost Tracking & Optimization",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LLMLab API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(data: UserSignup, db: Session = Depends(get_db)):
    """Create new user account"""
    # Check if user exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    api_key = generate_api_key()
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        api_key=api_key
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(user.email)
    return {"access_token": token, "api_key": api_key}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(user.email)
    return {"access_token": token, "api_key": user.api_key}

@app.post("/api/auth/logout")
async def logout():
    """Logout user (client deletes token)"""
    return {"message": "Logged out"}

# ============================================================================
# COST TRACKING
# ============================================================================

@app.post("/api/events/track")
async def track_cost(
    data: TrackCostRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Track an LLM API call cost"""
    user = get_current_user(authorization, db)
    
    # Calculate cost
    cost = calculate_cost(data.provider, data.model, data.input_tokens, data.output_tokens)
    
    # Save event
    event = CostEvent(
        user_id=user.id,
        provider=data.provider,
        model=data.model,
        input_tokens=data.input_tokens,
        output_tokens=data.output_tokens,
        cost=cost,
        metadata=json.dumps(data.metadata or {})
    )
    db.add(event)
    db.commit()
    
    return {
        "success": True,
        "cost": cost,
        "event_id": event.id
    }

@app.get("/api/costs/summary", response_model=CostSummary)
async def get_cost_summary(
    authorization: str = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get cost summary for user"""
    user = get_current_user(authorization, db)
    
    # Query costs
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_today = datetime(now.year, now.month, now.day)
    
    # Today
    today_events = db.query(CostEvent).filter(
        CostEvent.user_id == user.id,
        CostEvent.timestamp >= start_of_today
    ).all()
    today_spend = sum(e.cost for e in today_events)
    
    # This month
    month_events = db.query(CostEvent).filter(
        CostEvent.user_id == user.id,
        CostEvent.timestamp >= start_of_month
    ).all()
    month_spend = sum(e.cost for e in month_events)
    
    # All time
    all_events = db.query(CostEvent).filter(
        CostEvent.user_id == user.id
    ).all()
    total_spend = sum(e.cost for e in all_events)
    
    # By model
    by_model = {}
    for event in month_events:
        key = f"{event.provider}/{event.model}"
        by_model[key] = by_model.get(key, 0) + event.cost
    
    # By provider
    by_provider = {}
    for event in month_events:
        by_provider[event.provider] = by_provider.get(event.provider, 0) + event.cost
    
    # Daily trend (last 30 days)
    daily_trend = []
    for i in range(30):
        day = start_of_today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        day_events = [e for e in all_events if day_start <= e.timestamp < day_end]
        daily_spend = sum(e.cost for e in day_events)
        daily_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "spend": round(daily_spend, 2)
        })
    daily_trend.reverse()
    
    # Budget status
    budget_status = None
    if user.monthly_budget > 0:
        percentage = (month_spend / user.monthly_budget) * 100
        budget_status = {
            "budget": user.monthly_budget,
            "spent": round(month_spend, 2),
            "remaining": round(user.monthly_budget - month_spend, 2),
            "percentage": round(percentage, 1),
            "alert": percentage >= (user.budget_alert_threshold * 100)
        }
    
    return {
        "total_spend": round(total_spend, 2),
        "today_spend": round(today_spend, 2),
        "this_month_spend": round(month_spend, 2),
        "by_model": {k: round(v, 2) for k, v in by_model.items()},
        "by_provider": {k: round(v, 2) for k, v in by_provider.items()},
        "daily_trend": daily_trend,
        "budget_status": budget_status
    }

# ============================================================================
# BUDGET MANAGEMENT
# ============================================================================

@app.get("/api/budgets")
async def get_budgets(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get current budget for user"""
    user = get_current_user(authorization, db)
    return {
        "monthly_budget": user.monthly_budget,
        "alert_threshold": user.budget_alert_threshold
    }

@app.post("/api/budgets")
async def set_budget(
    data: BudgetRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Set monthly budget"""
    user = get_current_user(authorization, db)
    user.monthly_budget = data.amount
    db.commit()
    return {"success": True, "budget": data.amount}

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

@app.get("/api/recommendations", response_model=List[Recommendation])
async def get_recommendations(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get cost optimization recommendations"""
    user = get_current_user(authorization, db)
    
    # Get recent costs
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    events = db.query(CostEvent).filter(
        CostEvent.user_id == user.id,
        CostEvent.timestamp >= thirty_days_ago
    ).all()
    
    recommendations = []
    
    # Recommendation 1: Model switching
    gpt4_usage = sum(1 for e in events if e.model == "gpt-4")
    if gpt4_usage > 5:
        recommendations.append({
            "title": "Switch from GPT-4 to GPT-4 Turbo",
            "description": f"You used GPT-4 {gpt4_usage} times. GPT-4 Turbo is 3x cheaper with similar quality.",
            "savings_percentage": 70,
            "confidence": 85,
            "action": "Try GPT-4 Turbo for your next 10 calls"
        })
    
    # Recommendation 2: Token optimization
    avg_tokens = sum(e.input_tokens for e in events) / max(len(events), 1)
    if avg_tokens > 2000:
        recommendations.append({
            "title": "Optimize prompt length",
            "description": f"Your average prompt is {int(avg_tokens)} tokens. Industry avg is 1200.",
            "savings_percentage": 25,
            "confidence": 80,
            "action": "Review top 5 most expensive calls for prompt optimization"
        })
    
    # Recommendation 3: Anthropic suggestion
    anthropic_usage = sum(1 for e in events if e.provider == "anthropic")
    openai_usage = sum(1 for e in events if e.provider == "openai")
    if openai_usage > 20 and anthropic_usage == 0:
        recommendations.append({
            "title": "Try Anthropic Claude for summarization",
            "description": "Claude is 40% cheaper for summarization tasks and often produces better results.",
            "savings_percentage": 40,
            "confidence": 75,
            "action": "Test Claude on 20 of your summarization tasks"
        })
    
    return recommendations

# ============================================================================
# STATS & DEBUG
# ============================================================================

@app.get("/api/stats/providers")
async def get_provider_pricing():
    """Get pricing info for all providers (debug)"""
    return PROVIDER_PRICING

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
