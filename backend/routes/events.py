"""Event tracking routes."""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from models import EventTrackRequest, EventResponse
from database import get_db
from engines import CostCalculationEngine
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

# Mock event storage (in production, use Supabase)
events_storage = {}

cost_engine = CostCalculationEngine()


@router.post("/track", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def track_event(
    request_body: EventTrackRequest,
    request: Request,
    db=Depends(get_db)
):
    """
    Track LLM API call event.
    
    Args:
        request_body: Event tracking data
        request: FastAPI request object (contains user_id in state)
        db: Database client
    
    Returns:
        EventResponse with tracked event details
    """
    try:
        # Get user_id from auth middleware
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Calculate cost if not provided
        cost = request_body.cost
        if cost is None:
            cost = cost_engine.calculate_call_cost(
                provider=request_body.provider.value,
                model=request_body.model,
                input_tokens=request_body.input_tokens,
                output_tokens=request_body.output_tokens,
            )
        
        # Set timestamp
        timestamp = request_body.timestamp or datetime.now()
        
        # Store event
        event_data = {
            "event_id": event_id,
            "user_id": user_id,
            "provider": request_body.provider.value,
            "model": request_body.model,
            "input_tokens": request_body.input_tokens,
            "output_tokens": request_body.output_tokens,
            "total_tokens": request_body.input_tokens + request_body.output_tokens,
            "cost": cost,
            "metadata": request_body.metadata or {},
            "timestamp": timestamp,
        }
        
        events_storage[event_id] = event_data
        
        logger.info(
            f"Event tracked - User: {user_id}, Model: {request_body.model}, "
            f"Cost: ${cost:.4f}"
        )
        
        return EventResponse(
            event_id=event_id,
            user_id=user_id,
            provider=request_body.provider.value,
            model=request_body.model,
            total_tokens=request_body.input_tokens + request_body.output_tokens,
            cost=cost,
            tracked_at=timestamp,
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Event tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track event"
        )


@router.get("/")
async def list_events(request: Request, db=Depends(get_db)):
    """
    List all events for the user.
    
    Args:
        request: FastAPI request object
        db: Database client
    
    Returns:
        List of events
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        user_events = [
            event for event in events_storage.values()
            if event["user_id"] == user_id
        ]
        
        return {
            "count": len(user_events),
            "events": user_events,
        }
    
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list events"
        )
