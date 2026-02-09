"""Anthropic provider implementation."""

from .base import BaseProvider
from typing import Tuple


class AnthropicProvider(BaseProvider):
    """Anthropic API provider."""
    
    def __init__(self):
        """Initialize Anthropic provider with model pricing."""
        super().__init__("anthropic")
        
        # Pricing as of Feb 2024 (in USD per 1000 tokens)
        self.pricing = {
            "claude-3-opus": {
                "input": 0.015,
                "output": 0.075,
            },
            "claude-3-sonnet": {
                "input": 0.003,
                "output": 0.015,
            },
            "claude-3-haiku": {
                "input": 0.00025,
                "output": 0.00125,
            },
            "claude-2.1": {
                "input": 0.008,
                "output": 0.024,
            },
            "claude-2": {
                "input": 0.008,
                "output": 0.024,
            },
        }
    
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        """Get pricing for Anthropic model."""
        if model in self.pricing:
            pricing = self.pricing[model]
            return pricing["input"], pricing["output"]
        
        # Default to claude-3-haiku pricing if not found
        default = self.pricing["claude-3-haiku"]
        return default["input"], default["output"]
    
    def validate_model(self, model: str) -> bool:
        """Validate Anthropic model."""
        return model in self.pricing or model.startswith("claude-")
