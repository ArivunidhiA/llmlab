"""Recommendations endpoint."""

from fastapi import APIRouter, Depends, Request, Query
from models import RecommendationsResponse
from database import get_db
from engines import RecommendationsEngine
from routes.events import events_storage
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

recommendations_engine = RecommendationsEngine()


@router.get("", response_model=RecommendationsResponse)
async def get_recommendations(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """
    Get cost optimization recommendations.
    
    Args:
        request: FastAPI request object
        days: Number of days to analyze
        db: Database client
    
    Returns:
        RecommendationsResponse with optimization suggestions
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
            f"Recommendations requested - User: {user_id}, "
            f"Days: {days}, Events: {len(user_events)}"
        )
        
        # Generate recommendations
        recommendations = recommendations_engine.generate_recommendations(
            events=user_events
        )
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise


@router.get("/anomalies")
async def detect_anomalies(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    threshold: float = Query(2.0, ge=1.0, le=5.0),
    db=Depends(get_db)
):
    """
    Detect spending anomalies.
    
    Args:
        request: FastAPI request object
        days: Number of days to analyze
        threshold: Z-score threshold for anomaly detection
        db: Database client
    
    Returns:
        List of detected anomalies
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
        
        # Detect anomalies
        anomalies = recommendations_engine.detect_anomalies(
            events=user_events,
            threshold_std_dev=threshold
        )
        
        logger.info(
            f"Anomalies detected - User: {user_id}, "
            f"Anomaly count: {len(anomalies)}"
        )
        
        return {
            "count": len(anomalies),
            "anomalies": anomalies,
            "analysis_period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise


@router.get("/model-switching")
async def get_model_recommendations(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db=Depends(get_db)
):
    """
    Get model switching recommendations.
    
    Args:
        request: FastAPI request object
        days: Number of days to analyze
        db: Database client
    
    Returns:
        List of recommended model switches
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
        
        # Get recommendations
        recommendations = recommendations_engine.get_model_switch_recommendations(
            events=user_events
        )
        
        # Calculate total potential savings
        total_savings = sum(rec.estimated_monthly_savings for rec in recommendations)
        
        logger.info(
            f"Model recommendations retrieved - User: {user_id}, "
            f"Recommendations: {len(recommendations)}, "
            f"Potential savings: ${total_savings:.2f}"
        )
        
        return {
            "count": len(recommendations),
            "recommendations": recommendations,
            "total_potential_savings": round(total_savings, 2),
        }
    
    except Exception as e:
        logger.error(f"Error getting model recommendations: {e}")
        raise
