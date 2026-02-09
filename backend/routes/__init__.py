"""API routes."""

from .auth import router as auth_router
from .events import router as events_router
from .costs import router as costs_router
from .budgets import router as budgets_router
from .recommendations import router as recommendations_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "events_router",
    "costs_router",
    "budgets_router",
    "recommendations_router",
    "health_router",
]
