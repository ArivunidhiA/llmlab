"""OpenAI provider implementation."""

from .base import BaseProvider
from typing import Tuple


class OpenAIProvider(BaseProvider):
    """OpenAI API provider."""
    
    def __init__(self):
        """Initialize OpenAI provider with model pricing."""
        super().__init__("openai")
        
        # Pricing as of Feb 2024 (in USD per 1000 tokens)
        self.pricing = {
            "gpt-4": {
                "input": 0.03,
                "output": 0.06,
            },
            "gpt-4-turbo": {
                "input": 0.01,
                "output": 0.03,
            },
            "gpt-3.5-turbo": {
                "input": 0.0005,
                "output": 0.0015,
            },
            "gpt-4o": {
                "input": 0.005,
                "output": 0.015,
            },
            "gpt-4o-mini": {
                "input": 0.00015,
                "output": 0.0006,
            },
        }
    
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        """Get pricing for OpenAI model."""
        if model in self.pricing:
            pricing = self.pricing[model]
            return pricing["input"], pricing["output"]
        
        # Default to gpt-3.5-turbo pricing if not found
        default = self.pricing["gpt-3.5-turbo"]
        return default["input"], default["output"]
    
    def validate_model(self, model: str) -> bool:
        """Validate OpenAI model."""
        return model in self.pricing or model.startswith("gpt-")
