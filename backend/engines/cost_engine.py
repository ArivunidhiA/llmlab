"""Cost calculation engine."""

from models import ProviderType, CostByModel, CostByDate, CostSummary
from providers import OpenAIProvider, AnthropicProvider, GoogleProvider
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CostCalculationEngine:
    """Engine for calculating and aggregating costs."""
    
    def __init__(self):
        """Initialize cost engine with providers."""
        self.providers = {
            ProviderType.OPENAI.value: OpenAIProvider(),
            ProviderType.ANTHROPIC.value: AnthropicProvider(),
            ProviderType.GOOGLE.value: GoogleProvider(),
        }
    
    def get_provider(self, provider_name: str):
        """Get provider instance."""
        provider_name = provider_name.lower()
        if provider_name not in self.providers:
            logger.warning(f"Unknown provider: {provider_name}")
            return None
        return self.providers[provider_name]
    
    def calculate_call_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for a single API call.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in USD
        """
        provider_instance = self.get_provider(provider)
        if not provider_instance:
            return 0.0
        
        return provider_instance.calculate_cost(model, input_tokens, output_tokens)
    
    def check_budget(self, current_spend: float, budget_limit: float) -> Tuple[str, float]:
        """
        Check if within budget and return status.
        
        Args:
            current_spend: Current spending amount
            budget_limit: Budget limit
        
        Returns:
            Tuple of (status, percentage_used)
        """
        if budget_limit == 0:
            return "ok", 0.0
        
        percentage = (current_spend / budget_limit) * 100
        
        if percentage >= 100:
            return "exceeded", percentage
        elif percentage >= 80:
            return "warning", percentage
        else:
            return "ok", percentage
    
    def aggregate_by_model(
        self,
        events: List[Dict]
    ) -> List[CostByModel]:
        """
        Aggregate costs by model.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            List of CostByModel objects
        """
        model_costs: Dict[Tuple[str, str], Dict] = {}
        
        for event in events:
            key = (event["model"], event["provider"])
            
            if key not in model_costs:
                model_costs[key] = {
                    "model": event["model"],
                    "provider": event["provider"],
                    "total_calls": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                }
            
            model_costs[key]["total_calls"] += 1
            model_costs[key]["total_tokens"] += event.get("input_tokens", 0) + event.get("output_tokens", 0)
            model_costs[key]["total_cost"] += event.get("cost", 0)
        
        return [CostByModel(**data) for data in model_costs.values()]
    
    def aggregate_by_date(
        self,
        events: List[Dict]
    ) -> List[CostByDate]:
        """
        Aggregate costs by date.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            List of CostByDate objects
        """
        date_costs: Dict[str, Dict] = {}
        
        for event in events:
            timestamp = event.get("timestamp")
            if isinstance(timestamp, datetime):
                date_str = timestamp.strftime("%Y-%m-%d")
            else:
                date_str = str(timestamp).split("T")[0]
            
            if date_str not in date_costs:
                date_costs[date_str] = {
                    "date": date_str,
                    "total_cost": 0.0,
                    "call_count": 0,
                }
            
            date_costs[date_str]["total_cost"] += event.get("cost", 0)
            date_costs[date_str]["call_count"] += 1
        
        # Sort by date
        sorted_dates = sorted(date_costs.items())
        return [CostByDate(**data) for _, data in sorted_dates]
    
    def generate_summary(
        self,
        events: List[Dict],
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None,
    ) -> CostSummary:
        """
        Generate cost summary.
        
        Args:
            events: List of event dictionaries
            date_range_start: Start date (YYYY-MM-DD)
            date_range_end: End date (YYYY-MM-DD)
        
        Returns:
            CostSummary object
        """
        if not events:
            return CostSummary(
                total_cost=0.0,
                call_count=0,
                average_cost_per_call=0.0,
                by_model=[],
                by_date=[],
                date_range_start=date_range_start or "",
                date_range_end=date_range_end or "",
            )
        
        total_cost = sum(event.get("cost", 0) for event in events)
        call_count = len(events)
        avg_cost = total_cost / call_count if call_count > 0 else 0.0
        
        # Default date range if not provided
        if not date_range_start:
            date_range_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not date_range_end:
            date_range_end = datetime.now().strftime("%Y-%m-%d")
        
        return CostSummary(
            total_cost=round(total_cost, 2),
            call_count=call_count,
            average_cost_per_call=round(avg_cost, 4),
            by_model=self.aggregate_by_model(events),
            by_date=self.aggregate_by_date(events),
            date_range_start=date_range_start,
            date_range_end=date_range_end,
        )
