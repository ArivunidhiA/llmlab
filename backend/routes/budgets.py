"""Budget management routes."""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from models import Budget, BudgetRequest, BudgetsResponse, BudgetStatus
from database import get_db
from engines import CostCalculationEngine
from datetime import datetime
from routes.events import events_storage
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

# Mock budget storage (in production, use Supabase)
budgets_storage = {}

cost_engine = CostCalculationEngine()


@router.get("", response_model=BudgetsResponse)
async def get_budgets(request: Request, db=Depends(get_db)):
    """
    Get all budgets for the user.
    
    Args:
        request: FastAPI request object
        db: Database client
    
    Returns:
        BudgetsResponse with user's budgets
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Get user budgets
        user_budgets = [
            budget for budget in budgets_storage.values()
            if budget["user_id"] == user_id
        ]
        
        # Update budget status and spending
        updated_budgets = []
        total_limits = 0.0
        total_spend = 0.0
        
        for budget_data in user_budgets:
            # Calculate current spend based on events
            current_spend = sum(
                event["cost"]
                for event in events_storage.values()
                if event["user_id"] == user_id
            )
            
            # Determine status
            status_val = "ok"
            if budget_data["limit"] > 0:
                percentage = (current_spend / budget_data["limit"]) * 100
                if percentage >= 100:
                    status_val = "exceeded"
                elif percentage >= 80:
                    status_val = "warning"
            
            budget = Budget(
                id=budget_data["id"],
                user_id=budget_data["user_id"],
                limit=budget_data["limit"],
                period=budget_data["period"],
                current_spend=current_spend,
                status=BudgetStatus(status_val),
                created_at=budget_data["created_at"],
                updated_at=datetime.now(),
            )
            
            updated_budgets.append(budget)
            total_limits += budget.limit
            total_spend += budget.current_spend
        
        logger.info(f"Budgets retrieved - User: {user_id}, Count: {len(updated_budgets)}")
        
        return BudgetsResponse(
            budgets=updated_budgets,
            total_limits=total_limits,
            total_spend=total_spend,
        )
    
    except Exception as e:
        logger.error(f"Error retrieving budgets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve budgets"
        )


@router.post("", response_model=Budget, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_request: BudgetRequest,
    request: Request,
    db=Depends(get_db)
):
    """
    Create or update a budget.
    
    Args:
        budget_request: Budget configuration
        request: FastAPI request object
        db: Database client
    
    Returns:
        Created budget
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        # Check if budget already exists for period
        existing = [
            b for b in budgets_storage.values()
            if b["user_id"] == user_id and b["period"] == budget_request.period
        ]
        
        if existing:
            # Update existing
            budget_id = existing[0]["id"]
            budgets_storage[budget_id]["limit"] = budget_request.limit
            budgets_storage[budget_id]["updated_at"] = datetime.now()
            budget_data = budgets_storage[budget_id]
        else:
            # Create new
            budget_id = str(uuid.uuid4())
            now = datetime.now()
            
            budget_data = {
                "id": budget_id,
                "user_id": user_id,
                "limit": budget_request.limit,
                "period": budget_request.period,
                "created_at": now,
                "updated_at": now,
            }
            
            budgets_storage[budget_id] = budget_data
        
        # Calculate current spend
        current_spend = sum(
            event["cost"]
            for event in events_storage.values()
            if event["user_id"] == user_id
        )
        
        # Determine status
        status_val = "ok"
        if budget_data["limit"] > 0:
            percentage = (current_spend / budget_data["limit"]) * 100
            if percentage >= 100:
                status_val = "exceeded"
            elif percentage >= 80:
                status_val = "warning"
        
        logger.info(
            f"Budget created/updated - User: {user_id}, "
            f"Period: {budget_request.period}, Limit: ${budget_request.limit}"
        )
        
        return Budget(
            id=budget_data["id"],
            user_id=budget_data["user_id"],
            limit=budget_data["limit"],
            period=budget_data["period"],
            current_spend=current_spend,
            status=BudgetStatus(status_val),
            created_at=budget_data["created_at"],
            updated_at=budget_data["updated_at"],
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create budget"
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    request: Request,
    db=Depends(get_db)
):
    """
    Delete a budget.
    
    Args:
        budget_id: Budget ID to delete
        request: FastAPI request object
        db: Database client
    """
    try:
        user_id = getattr(request.state, "user_id", "anonymous")
        
        if budget_id not in budgets_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        budget = budgets_storage[budget_id]
        
        if budget["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this budget"
            )
        
        del budgets_storage[budget_id]
        
        logger.info(f"Budget deleted - User: {user_id}, Budget: {budget_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete budget"
        )
