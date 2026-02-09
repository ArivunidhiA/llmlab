"""Tests for provider implementations."""

import pytest
from providers import OpenAIProvider, AnthropicProvider, GoogleProvider


class TestOpenAIProvider:
    """Test suite for OpenAI provider."""
    
    @pytest.fixture
    def provider(self):
        """Create OpenAI provider instance."""
        return OpenAIProvider()
    
    def test_model_validation(self, provider):
        """Test model validation."""
        assert provider.validate_model("gpt-4") is True
        assert provider.validate_model("gpt-3.5-turbo") is True
        assert provider.validate_model("gpt-4o") is True
        assert provider.validate_model("unknown-model") is True  # Starts with gpt-
        assert provider.validate_model("claude-3") is False
    
    def test_pricing_retrieval(self, provider):
        """Test getting model pricing."""
        input_price, output_price = provider.get_model_pricing("gpt-4")
        
        assert input_price == 0.03
        assert output_price == 0.06
    
    def test_default_pricing(self, provider):
        """Test default pricing for unknown model."""
        input_price, output_price = provider.get_model_pricing("gpt-unknown")
        
        # Should return gpt-3.5-turbo pricing as default
        assert input_price == 0.0005
        assert output_price == 0.0015
    
    def test_list_models(self, provider):
        """Test listing available models."""
        models = provider.list_models()
        
        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models
        assert len(models) > 0
    
    def test_cost_calculation(self, provider):
        """Test cost calculation."""
        cost = provider.calculate_cost("gpt-3.5-turbo", 1000, 500)
        
        # (1000/1000)*0.0005 + (500/1000)*0.0015 = 0.0005 + 0.00075 = 0.00125
        assert cost == pytest.approx(0.00125, rel=1e-6)


class TestAnthropicProvider:
    """Test suite for Anthropic provider."""
    
    @pytest.fixture
    def provider(self):
        """Create Anthropic provider instance."""
        return AnthropicProvider()
    
    def test_model_validation(self, provider):
        """Test model validation."""
        assert provider.validate_model("claude-3-opus") is True
        assert provider.validate_model("claude-3-sonnet") is True
        assert provider.validate_model("claude-2") is True
        assert provider.validate_model("claude-unknown") is True  # Starts with claude-
        assert provider.validate_model("gpt-4") is False
    
    def test_pricing_retrieval(self, provider):
        """Test getting model pricing."""
        input_price, output_price = provider.get_model_pricing("claude-3-opus")
        
        assert input_price == 0.015
        assert output_price == 0.075
    
    def test_cost_calculation(self, provider):
        """Test cost calculation."""
        cost = provider.calculate_cost("claude-3-haiku", 2000, 1000)
        
        # (2000/1000)*0.00025 + (1000/1000)*0.00125 = 0.0005 + 0.00125 = 0.00175
        assert cost == pytest.approx(0.00175, rel=1e-6)


class TestGoogleProvider:
    """Test suite for Google provider."""
    
    @pytest.fixture
    def provider(self):
        """Create Google provider instance."""
        return GoogleProvider()
    
    def test_model_validation(self, provider):
        """Test model validation."""
        assert provider.validate_model("gemini-pro") is True
        assert provider.validate_model("gemini-1.5-pro") is True
        assert provider.validate_model("gemini-unknown") is True  # Starts with gemini-
        assert provider.validate_model("gpt-4") is False
    
    def test_pricing_retrieval(self, provider):
        """Test getting model pricing."""
        input_price, output_price = provider.get_model_pricing("gemini-1.5-pro")
        
        assert input_price == 0.0035
        assert output_price == 0.0105
    
    def test_cost_calculation(self, provider):
        """Test cost calculation."""
        cost = provider.calculate_cost("gemini-pro", 1000, 1000)
        
        # (1000/1000)*0.00025 + (1000/1000)*0.0005 = 0.00025 + 0.0005 = 0.00075
        assert cost == pytest.approx(0.00075, rel=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
