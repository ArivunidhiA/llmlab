"""Google provider implementation."""

from .base import BaseProvider
from typing import Tuple


class GoogleProvider(BaseProvider):
    """Google Gemini API provider."""
    
    def __init__(self):
        """Initialize Google provider with model pricing."""
        super().__init__("google")
        
        # Pricing as of Feb 2024 (in USD per 1000 tokens)
        self.pricing = {
            "gemini-pro": {
                "input": 0.00025,
                "output": 0.0005,
            },
            "gemini-1.5-pro": {
                "input": 0.0035,
                "output": 0.0105,
            },
            "gemini-1.5-flash": {
                "input": 0.00025,
                "output": 0.00075,
            },
            "palm-2": {
                "input": 0.0005,
                "output": 0.0005,
            },
        }
    
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        """Get pricing for Google model."""
        if model in self.pricing:
            pricing = self.pricing[model]
            return pricing["input"], pricing["output"]
        
        # Default to gemini-pro pricing if not found
        default = self.pricing["gemini-pro"]
        return default["input"], default["output"]
    
    def validate_model(self, model: str) -> bool:
        """Validate Google model."""
        return model in self.pricing or model.startswith("gemini-")
