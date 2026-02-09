"""Base provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, name: str):
        """Initialize provider."""
        self.name = name
        self.pricing: Dict[str, Dict[str, float]] = {}  # {model: {input: price, output: price}}
    
    @abstractmethod
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        """
        Get pricing for a model.
        
        Returns:
            Tuple of (input_price_per_1k_tokens, output_price_per_1k_tokens)
        """
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Check if model is valid for this provider."""
        pass
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate total cost for API call.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Total cost in USD
        """
        if not self.validate_model(model):
            logger.warning(f"Unknown model {model} for provider {self.name}")
            return 0.0
        
        input_price, output_price = self.get_model_pricing(model)
        
        # Calculate cost (prices are per 1000 tokens)
        input_cost = (input_tokens / 1000) * input_price
        output_cost = (output_tokens / 1000) * output_price
        
        return round(input_cost + output_cost, 6)
    
    def list_models(self) -> list:
        """List all models supported by this provider."""
        return list(self.pricing.keys())
