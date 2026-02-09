"""SQLAlchemy ORM models"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notification preferences
    slack_webhook = Column(String, nullable=True)
    discord_webhook = Column(String, nullable=True)
    email_alerts = Column(Boolean, default=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")


class APIKey(Base):
    """API keys for users"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # openai, anthropic, google, cohere
    encrypted_key = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)  # For display (e.g., sk-...)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Event(Base):
    """LLM API call events"""
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Event metadata
    provider = Column(String, nullable=False)  # openai, anthropic, google, cohere
    model = Column(String, nullable=False, index=True)
    
    # Token counts
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    
    # Timing
    duration_ms = Column(Float, default=0.0)
    
    # Request metadata
    request_metadata = Column(JSON, default={})  # Custom fields
    
    # Cost calculation
    calculated_cost = Column(Float, default=0.0, index=True)  # USD
    currency = Column(String, default="USD")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="events")


class Budget(Base):
    """User budget configurations"""
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Budget limits
    monthly_limit = Column(Float, nullable=False)  # USD
    period = Column(String, default="monthly")  # monthly, weekly
    
    # Alert thresholds
    alert_at_50 = Column(Boolean, default=True)
    alert_at_80 = Column(Boolean, default=True)
    alert_at_100 = Column(Boolean, default=True)
    
    # Notification channels
    alert_channel = Column(String, default="email")  # email, slack, discord
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")


class AlertLog(Base):
    """Log of sent alerts"""
    __tablename__ = "alert_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String)  # 50%, 80%, 100%
    current_spend = Column(Float)
    limit = Column(Float)
    
    # Channel info
    channel = Column(String)  # email, slack, discord
    sent_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
