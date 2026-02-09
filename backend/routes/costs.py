"""Cost summary and reporting routes."""

from fastapi import APIRouter, Depends, Request, Query
from models import CostSummary
from database import get_db
from engines import CostCalculationEngine
from datetime import datetime, timedelta
from routes.events import events_storage
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/costs", tags=["costs"])

cost_engine = CostCalculationEngine()


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """
    Get cost summary for the user.
    
    Args:
        request: FastAPI request object
        days: Number of days to include in summary (default: 30)
        db: Database client
    
    Returns:
        CostSummary with aggregated costs
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter events for user and date range
        user_events = [
            event for event in events_storage.values()
            if event["user_id"] == user_id
            and start_date <= event["timestamp"] <= end_date
        ]
        
        logger.info(
            f"Cost summary requested - User: {user_id}, "
            f"Days: {days}, Events: {len(user_events)}"
        )
        
        # Generate summary
        summary = cost_engine.generate_summary(
            events=user_events,
            date_range_start=start_date.strftime("%Y-%m-%d"),
            date_range_end=end_date.strftime("%Y-%m-%d"),
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating cost summary: {e}")
        raise


@router.get("/by-provider")
async def get_costs_by_provider(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """
    Get costs broken down by provider.
    
    Args:
        request: FastAPI request object
        days: Number of days to include
        db: Database client
    
    Returns:
        Costs aggregated by provider
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter events
        user_events = [
            event for event in events_storage.values()
            if event["user_id"] == user_id
            and start_date <= event["timestamp"] <= end_date
        ]
        
        # Group by provider
        provider_costs = {}
        
        for event in user_events:
            provider = event["provider"]
            
            if provider not in provider_costs:
                provider_costs[provider] = {
                    "provider": provider,
                    "total_cost": 0.0,
                    "call_count": 0,
                    "models": {},
                }
            
            provider_costs[provider]["total_cost"] += event["cost"]
            provider_costs[provider]["call_count"] += 1
            
            # Track models within provider
            model = event["model"]
            if model not in provider_costs[provider]["models"]:
                provider_costs[provider]["models"][model] = {
                    "cost": 0.0,
                    "calls": 0,
                }
            
            provider_costs[provider]["models"][model]["cost"] += event["cost"]
            provider_costs[provider]["models"][model]["calls"] += 1
        
        return {
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
            "provider_costs": list(provider_costs.values()),
        }
    
    except Exception as e:
        logger.error(f"Error getting provider costs: {e}")
        raise


@router.get("/top-models")
async def get_top_models(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """
    Get top N most expensive models.
    
    Args:
        request: FastAPI request object
        limit: Number of models to return
        days: Number of days to include
        db: Database client
    
    Returns:
        List of top models by cost
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter events
        user_events = [
            event for event in events_storage.values()
            if event["user_id"] == user_id
            and start_date <= event["timestamp"] <= end_date
        ]
        
        # Get cost by model
        by_model = cost_engine.aggregate_by_model(user_events)
        
        # Sort by cost and limit
        sorted_models = sorted(
            by_model,
            key=lambda x: x.total_cost,
            reverse=True
        )[:limit]
        
        return {
            "count": len(sorted_models),
            "models": sorted_models,
        }
    
    except Exception as e:
        logger.error(f"Error getting top models: {e}")
        raise
