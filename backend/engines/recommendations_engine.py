"""Recommendations engine for cost optimization."""

from models import CostOptimization, Recommendation, RecommendationsResponse
from providers import OpenAIProvider, AnthropicProvider, GoogleProvider
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics
import logging

logger = logging.getLogger(__name__)


class RecommendationsEngine:
    """Engine for generating cost optimization recommendations."""
    
    def __init__(self):
        """Initialize recommendations engine."""
        self.openai = OpenAIProvider()
        self.anthropic = AnthropicProvider()
        self.google = GoogleProvider()
    
    def detect_anomalies(
        self,
        events: List[Dict],
        threshold_std_dev: float = 2.0
    ) -> List[Dict]:
        """
        Detect spending anomalies.
        
        Args:
            events: List of event dictionaries with costs
            threshold_std_dev: Number of standard deviations for anomaly detection
        
        Returns:
            List of anomalies detected
        """
        if len(events) < 3:
            return []
        
        costs = [event.get("cost", 0) for event in events]
        
        try:
            mean_cost = statistics.mean(costs)
            std_dev = statistics.stdev(costs)
            
            if std_dev == 0:
                return []
            
            anomalies = []
            for event in events:
                cost = event.get("cost", 0)
                z_score = abs((cost - mean_cost) / std_dev)
                
                if z_score > threshold_std_dev:
                    anomalies.append({
                        "event_id": event.get("id"),
                        "model": event.get("model"),
                        "cost": cost,
                        "z_score": round(z_score, 2),
                        "severity": "high" if z_score > 3 else "medium",
                    })
            
            return anomalies
        except (ValueError, statistics.StatisticsError):
            return []
    
    def get_model_switch_recommendations(
        self,
        events: List[Dict]
    ) -> List[Recommendation]:
        """
        Generate model switching recommendations.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Group by model and calculate costs
        model_stats: Dict[str, Dict] = {}
        
        for event in events:
            model = event.get("model")
            provider = event.get("provider")
            cost = event.get("cost", 0)
            
            if model not in model_stats:
                model_stats[model] = {
                    "provider": provider,
                    "costs": [],
                    "calls": 0,
                }
            
            model_stats[model]["costs"].append(cost)
            model_stats[model]["calls"] += 1
        
        # For expensive models, suggest cheaper alternatives
        expensive_models = {
            "gpt-4": {
                "alternative": "gpt-4-turbo",
                "provider": "openai",
                "use_case": "Complex reasoning, document analysis",
            },
            "claude-3-opus": {
                "alternative": "claude-3-sonnet",
                "provider": "anthropic",
                "use_case": "General purpose, coding",
            },
            "gemini-1.5-pro": {
                "alternative": "gemini-1.5-flash",
                "provider": "google",
                "use_case": "Quick responses, summarization",
            },
        }
        
        for model, stats in model_stats.items():
            if model in expensive_models:
                alt_config = expensive_models[model]
                
                # Get pricing
                provider = self._get_provider(stats["provider"])
                alt_provider = self._get_provider(alt_config["provider"])
                
                if provider and alt_provider:
                    current_input, current_output = provider.get_model_pricing(model)
                    alt_input, alt_output = alt_provider.get_model_pricing(alt_config["alternative"])
                    
                    # Estimate monthly savings
                    avg_input_tokens = 500  # Assumption
                    avg_output_tokens = 500  # Assumption
                    monthly_calls = stats["calls"]
                    
                    current_monthly = (
                        (avg_input_tokens / 1000) * current_input +
                        (avg_output_tokens / 1000) * current_output
                    ) * monthly_calls
                    
                    alt_monthly = (
                        (avg_input_tokens / 1000) * alt_input +
                        (avg_output_tokens / 1000) * alt_output
                    ) * monthly_calls
                    
                    savings = current_monthly - alt_monthly
                    
                    if savings > 0:
                        recommendations.append(
                            Recommendation(
                                current_model=model,
                                suggested_model=alt_config["alternative"],
                                current_cost_per_call=round(current_input + current_output, 6),
                                suggested_cost_per_call=round(alt_input + alt_output, 6),
                                estimated_monthly_savings=round(savings, 2),
                                use_case=alt_config["use_case"],
                            )
                        )
        
        return recommendations
    
    def get_cost_optimizations(
        self,
        events: List[Dict]
    ) -> List[CostOptimization]:
        """
        Generate general cost optimization recommendations.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            List of optimization recommendations
        """
        optimizations = []
        
        if not events:
            return optimizations
        
        # Optimization 1: Batch Processing
        call_count = len(events)
        if call_count > 10:
            optimizations.append(
                CostOptimization(
                    type="batch_processing",
                    title="Implement Batch Processing",
                    description="Group multiple requests together to reduce API overhead and potential rate limiting.",
                    potential_savings=round(call_count * 0.1, 2),  # Estimate 10% savings
                    priority="medium",
                )
            )
        
        # Optimization 2: Caching
        optimizations.append(
            CostOptimization(
                type="caching",
                title="Implement Response Caching",
                description="Cache API responses for repeated queries to avoid redundant API calls.",
                potential_savings=round(call_count * 0.15, 2),  # Estimate 15% savings
                priority="high",
            )
        )
        
        # Optimization 3: Token Optimization
        total_tokens = sum(
            event.get("input_tokens", 0) + event.get("output_tokens", 0)
            for event in events
        )
        
        if total_tokens > 100000:
            optimizations.append(
                CostOptimization(
                    type="token_optimization",
                    title="Optimize Token Usage",
                    description="Reduce token consumption by removing unnecessary context, summarizing inputs, and using shorter prompts.",
                    potential_savings=round(total_tokens * 0.08, 2),  # Estimate 8% savings
                    priority="high",
                )
            )
        
        # Optimization 4: Model Selection
        optimizations.append(
            CostOptimization(
                type="model_selection",
                title="Use Task-Specific Models",
                description="Use smaller, cheaper models for simpler tasks instead of always using the most powerful model.",
                potential_savings=round(call_count * 0.20, 2),  # Estimate 20% savings
                priority="high",
            )
        )
        
        return optimizations
    
    def _get_provider(self, provider_name: str):
        """Get provider instance."""
        provider_name = provider_name.lower()
        if provider_name == "openai":
            return self.openai
        elif provider_name == "anthropic":
            return self.anthropic
        elif provider_name == "google":
            return self.google
        return None
    
    def generate_recommendations(
        self,
        events: List[Dict]
    ) -> RecommendationsResponse:
        """
        Generate all recommendations.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            RecommendationsResponse with all recommendations
        """
        return RecommendationsResponse(
            optimizations=self.get_cost_optimizations(events),
            model_recommendations=self.get_model_switch_recommendations(events),
            anomalies=self.detect_anomalies(events),
            last_updated=datetime.now(),
        )
