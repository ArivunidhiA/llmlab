# LLMLab Extensibility & Integration Roadmap

**Version:** 1.0 (Future Capabilities)  
**Status:** Plugin Architecture Specification  
**Target:** Enable community contributions at scale  

---

## INTRODUCTION

LLMLab is designed for **maximum extensibility** at three levels:

1. **Provider Plugins** — Add new LLM cost providers (Cohere, Hugging Face, custom APIs)
2. **Integration Plugins** — Connect to external tools (Slack, Discord, DataDog, etc.)
3. **Custom Evals** — Domain-specific compliance checks (industry regulations, custom metrics)

This document outlines the plugin system, interface standards, and community contribution guidelines.

---

## PART 1: PROVIDER PLUGIN SYSTEM

### Overview

**Current Supported Providers:**
- OpenAI
- Anthropic
- Azure OpenAI
- Google Gemini

**Roadmap (Future Providers):**
- Cohere
- Hugging Face
- Mistral AI
- TogetherAI
- Custom / Self-Hosted

### Plugin Interface Specification

All providers implement the `ProviderBase` abstract class:

```python
# llmlab/providers/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CostRecord:
    """Standard cost record format"""
    provider: str
    model: str
    timestamp: datetime
    cost_usd: float
    input_tokens: int
    output_tokens: int
    api_call_id: str
    metadata: Dict = None
    status: str = 'success'
    error_message: Optional[str] = None

@dataclass
class ModelInfo:
    """Model information"""
    name: str
    pricing_input: float    # Cost per 1K input tokens
    pricing_output: float   # Cost per 1K output tokens
    context_window: int
    max_output_tokens: int
    release_date: str

class ProviderBase(ABC):
    """Abstract base class for LLM cost providers"""
    
    PROVIDER_NAME: str  # Unique identifier: "openai", "cohere", etc.
    DISPLAY_NAME: str   # Human-friendly: "OpenAI", "Cohere", etc.
    
    def __init__(self, api_key: str, **credentials):
        """Initialize provider with credentials
        
        Args:
            api_key: Primary API key
            **credentials: Additional provider-specific credentials
                e.g., organization_id for OpenAI, workspace_id for Cohere
        """
        self.api_key = api_key
        self.credentials = credentials
    
    @abstractmethod
    async def fetch_costs(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[CostRecord]:
        """Fetch cost records from provider API
        
        Args:
            start_date: Start of period
            end_date: End of period
        
        Returns:
            List of CostRecord objects
        
        Raises:
            ProviderAuthError: Invalid credentials
            ProviderRateLimitError: Rate limited
            ProviderAPIError: Generic API error
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Test if credentials are valid
        
        Should make minimal API call to verify authentication
        
        Returns:
            True if valid, False otherwise
        
        Raises:
            ProviderAuthError: If invalid
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """List available models
        
        Returns:
            List of model names/IDs
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model: str) -> ModelInfo:
        """Get detailed information about a model
        
        Args:
            model: Model name/ID
        
        Returns:
            ModelInfo with pricing and specs
        """
        pass
    
    @abstractmethod
    async def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for a hypothetical request
        
        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
        
        Returns:
            Estimated cost in USD
        """
        pass
    
    def get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing for a model
        
        Returns:
            {
                'input': cost_per_1k_tokens,
                'output': cost_per_1k_tokens
            }
        """
        info = self.get_model_info(model)
        return {
            'input': info.pricing_input,
            'output': info.pricing_output
        }
```

### Example: Creating a Cohere Provider

**File:** `llmlab/providers/cohere_provider.py`

```python
import httpx
from datetime import datetime
from typing import List

from llmlab.providers.base import ProviderBase, CostRecord, ModelInfo
from llmlab.exceptions import ProviderAuthError, ProviderAPIError

class CohereProvider(ProviderBase):
    """Cohere API cost provider"""
    
    PROVIDER_NAME = "cohere"
    DISPLAY_NAME = "Cohere"
    API_BASE = "https://api.cohere.ai/v1"
    
    # Current Cohere pricing (updated quarterly)
    MODELS = {
        "command-r-v1:10k-temp": {
            "input": 0.005,
            "output": 0.015,
            "context_window": 128000,
            "max_output_tokens": 4096
        },
        "command-r-plus": {
            "input": 0.03,
            "output": 0.1,
            "context_window": 128000,
            "max_output_tokens": 4096
        },
        "command": {
            "input": 0.001,
            "output": 0.002,
            "context_window": 4096,
            "max_output_tokens": 4096
        }
    }
    
    async def fetch_costs(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch costs from Cohere Billing API
        
        Note: Cohere doesn't expose billing API yet
        Workaround: Use SDK instrumentation + billing exports
        """
        
        # TODO: Once Cohere exposes billing API
        # GET /accounts/billing/usage
        
        # For now, return empty (users can upload CSV exports manually)
        return []
    
    async def validate_credentials(self) -> bool:
        """Test Cohere API key with simple request"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE}/chat",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"only_deployments": True},
                    timeout=5.0
                )
                
                if response.status_code == 401:
                    raise ProviderAuthError("Invalid Cohere API key")
                
                response.raise_for_status()
                return True
        
        except httpx.HTTPError as e:
            raise ProviderAPIError(f"Cohere API error: {e}")
    
    def get_models(self) -> List[str]:
        """List available Cohere models"""
        return list(self.MODELS.keys())
    
    def get_model_info(self, model: str) -> ModelInfo:
        """Get model specifications"""
        
        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}")
        
        pricing = self.MODELS[model]
        
        return ModelInfo(
            name=model,
            pricing_input=pricing['input'],
            pricing_output=pricing['output'],
            context_window=pricing['context_window'],
            max_output_tokens=pricing['max_output_tokens'],
            release_date="2024-01-15"
        )
    
    async def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for a request"""
        
        pricing = self.MODELS.get(model)
        if not pricing:
            raise ValueError(f"Unknown model: {model}")
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
```

### Registering a Custom Provider

**File:** `llmlab/config/providers.py`

```python
from llmlab.providers.openai_provider import OpenAIProvider
from llmlab.providers.anthropic_provider import AnthropicProvider
from llmlab.providers.cohere_provider import CohereProvider

PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "cohere": CohereProvider,
}

def register_provider(provider_name: str, provider_class):
    """Register a custom provider"""
    PROVIDER_REGISTRY[provider_name] = provider_class

def get_provider(provider_name: str, api_key: str, **credentials):
    """Get provider instance"""
    if provider_name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    provider_class = PROVIDER_REGISTRY[provider_name]
    return provider_class(api_key, **credentials)
```

### Dashboard Integration

**File:** `frontend/config/providers.ts`

```typescript
export interface ProviderConfig {
  value: string;
  label: string;
  description: string;
  docLink: string;
  credentialFields: {
    name: string;
    type: 'text' | 'password' | 'select';
    label: string;
    required: boolean;
  }[];
}

export const PROVIDER_OPTIONS: ProviderConfig[] = [
  {
    value: 'openai',
    label: 'OpenAI',
    description: 'GPT-4, GPT-3.5-Turbo, Embeddings',
    docLink: '/docs/providers/openai',
    credentialFields: [
      {
        name: 'api_key',
        type: 'password',
        label: 'API Key',
        required: true
      },
      {
        name: 'organization_id',
        type: 'text',
        label: 'Organization ID',
        required: false
      }
    ]
  },
  {
    value: 'cohere',
    label: 'Cohere',
    description: 'Command, Command-R, Embeddings',
    docLink: '/docs/providers/cohere',
    credentialFields: [
      {
        name: 'api_key',
        type: 'password',
        label: 'API Key',
        required: true
      }
    ]
  }
];
```

---

## PART 2: INTEGRATION PLUGINS

### Overview

Integrations connect LLMLab to external services:

**Built-In (MVP):**
- Email notifications
- Slack webhooks

**Roadmap (Community):**
- Discord
- Teams
- DataDog
- New Relic
- Custom webhooks
- GitHub Actions

### Integration Interface

```python
# llmlab/integrations/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class IntegrationBase(ABC):
    """Abstract base class for integrations"""
    
    INTEGRATION_NAME: str
    DISPLAY_NAME: str
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize integration with config
        
        Args:
            config: Integration-specific configuration
                {
                    'webhook_url': '...',
                    'channel': '#alerts',
                    ...
                }
        """
        self.config = config
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """Test if configuration is valid"""
        pass
    
    @abstractmethod
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert notification
        
        Args:
            alert_data: {
                'type': 'budget_threshold',
                'project_name': 'Production Chatbot',
                'threshold': 80,
                'current_spend': 800,
                'budget': 1000,
                'timestamp': '2024-01-15T10:30:00Z'
            }
        
        Returns:
            True if sent successfully
        """
        pass
    
    @abstractmethod
    async def send_recommendation(self, rec_data: Dict[str, Any]) -> bool:
        """Send a recommendation notification"""
        pass
```

### Example: Discord Integration

**File:** `llmlab/integrations/discord_integration.py`

```python
import httpx
import json
from typing import Dict, Any

from llmlab.integrations.base import IntegrationBase

class DiscordIntegration(IntegrationBase):
    """Discord webhook integration"""
    
    INTEGRATION_NAME = "discord"
    DISPLAY_NAME = "Discord"
    
    async def validate_config(self) -> bool:
        """Test Discord webhook"""
        
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json={
                        "content": "LLMLab integration test"
                    }
                )
                return response.status_code == 204
        except:
            return False
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert to Discord"""
        
        webhook_url = self.config.get('webhook_url')
        color = 0xFF6B6B if alert_data['type'] == 'error' else 0xFFA500
        
        embed = {
            "title": f"🚨 Budget Alert: {alert_data['project_name']}",
            "color": color,
            "fields": [
                {
                    "name": "Threshold Reached",
                    "value": f"{alert_data['threshold']}%",
                    "inline": True
                },
                {
                    "name": "Current Spend",
                    "value": f"${alert_data['current_spend']}",
                    "inline": True
                },
                {
                    "name": "Budget Limit",
                    "value": f"${alert_data['budget']}",
                    "inline": True
                }
            ],
            "timestamp": alert_data['timestamp']
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json={"embeds": [embed]}
                )
                return response.status_code == 204
        except:
            return False
```

### Registering Integrations

```python
# llmlab/config/integrations.py

from llmlab.integrations.slack_integration import SlackIntegration
from llmlab.integrations.discord_integration import DiscordIntegration
from llmlab.integrations.email_integration import EmailIntegration

INTEGRATION_REGISTRY = {
    "slack": SlackIntegration,
    "discord": DiscordIntegration,
    "email": EmailIntegration,
}

def register_integration(name: str, integration_class):
    INTEGRATION_REGISTRY[name] = integration_class
```

---

## PART 3: CUSTOM EVALS PLUGIN SYSTEM

### Overview

**Built-In Evals (MVP):**
- Cost comparison
- Accuracy metrics
- Latency benchmarks

**Roadmap (Community):**
- PII detection
- Hallucination detection
- Bias detection
- Industry-specific checks (custom validators)
- Custom domain evals

### Eval Interface

```python
# llmlab/evals/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class EvalResult:
    """Result of an evaluation"""
    name: str
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = None

class EvalBase(ABC):
    """Abstract base class for custom evals"""
    
    EVAL_NAME: str  # "pii_detection", "hallucination_check", etc.
    DISPLAY_NAME: str
    DESCRIPTION: str
    
    @abstractmethod
    async def evaluate(
        self,
        prompt: str,
        response: str,
        model: str,
        **context
    ) -> EvalResult:
        """Run evaluation
        
        Args:
            prompt: Input prompt
            response: LLM response
            model: Model used
            **context: Additional context (user_id, project_id, etc.)
        
        Returns:
            EvalResult with score and details
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for eval configuration"""
        pass
```

### Example: Custom PII Detection Eval

**File:** `llmlab/evals/pii_detection_eval.py`

```python
import re
from typing import Dict, Any, List

from llmlab.evals.base import EvalBase, EvalResult

class PIIDetectionEval(EvalBase):
    """Detect PII (personally identifiable information) in responses"""
    
    EVAL_NAME = "pii_detection"
    DISPLAY_NAME = "PII Detection"
    DESCRIPTION = "Check for leakage of personal information (emails, phone numbers, SSN, etc.)"
    
    # Patterns for common PII
    PII_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'(\d{3}[-.\s]?){2}\d{4}',
        'ssn': r'\d{3}-\d{2}-\d{4}',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    }
    
    async def evaluate(
        self,
        prompt: str,
        response: str,
        model: str,
        **context
    ) -> EvalResult:
        """Check response for PII"""
        
        findings = {}
        pii_found = False
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, response)
            if matches:
                pii_found = True
                findings[pii_type] = matches[:3]  # First 3 matches
        
        passed = not pii_found
        score = 1.0 if passed else 0.0
        
        return EvalResult(
            name=self.EVAL_NAME,
            passed=passed,
            score=score,
            message="No PII detected" if passed else f"PII detected: {list(findings.keys())}",
            details={'findings': findings}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            "type": "object",
            "properties": {
                "enabled_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": list(self.PII_PATTERNS.keys())},
                    "default": list(self.PII_PATTERNS.keys())
                }
            }
        }
```

### Registering Custom Evals

```python
# llmlab/config/evals.py

from llmlab.evals.pii_detection_eval import PIIDetectionEval
from llmlab.evals.hallucination_eval import HallucinationEval

EVAL_REGISTRY = {
    "pii_detection": PIIDetectionEval,
    "hallucination": HallucinationEval,
}

def register_eval(name: str, eval_class):
    """Register a custom eval"""
    EVAL_REGISTRY[name] = eval_class

def get_eval(name: str, config: Dict[str, Any]):
    """Get eval instance"""
    if name not in EVAL_REGISTRY:
        raise ValueError(f"Unknown eval: {name}")
    
    eval_class = EVAL_REGISTRY[name]
    return eval_class(config)
```

---

## PART 4: CONTRIBUTION GUIDELINES

### Submitting a New Provider

**Step 1: Create Provider Class**
```bash
# Fork LLMLab repo
git clone https://github.com/yourusername/llmlab.git
git checkout -b feature/add-cohere-provider

# Create provider
touch llmlab/providers/cohere_provider.py
```

**Step 2: Implement Interface**
- Inherit from `ProviderBase`
- Implement all abstract methods
- Add comprehensive docstrings
- Handle errors gracefully

**Step 3: Write Tests**
```python
# tests/test_cohere_provider.py

import pytest
from llmlab.providers.cohere_provider import CohereProvider

@pytest.mark.asyncio
async def test_validate_credentials():
    provider = CohereProvider(api_key="test_key")
    result = await provider.validate_credentials()
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_get_models():
    provider = CohereProvider(api_key="test_key")
    models = provider.get_models()
    assert len(models) > 0
    assert isinstance(models[0], str)
```

**Step 4: Register Provider**
- Add to `llmlab/config/providers.py`
- Update documentation

**Step 5: Submit PR**
```bash
git commit -m "feat: add Cohere cost provider"
git push origin feature/add-cohere-provider
# Create PR on GitHub
```

**PR Checklist:**
- [ ] Tests pass (`pytest`)
- [ ] Code follows style guide (`black`, `flake8`)
- [ ] Docstrings complete
- [ ] No API keys in code
- [ ] Example usage documented

### Provider Contribution Template

```python
# Template for new provider

class NewProviderName(ProviderBase):
    """
    [Provider Name] cost provider
    
    Features:
    - [Feature 1]
    - [Feature 2]
    
    Documentation: https://provider-docs-link
    """
    
    PROVIDER_NAME = "provider_name"
    DISPLAY_NAME = "Provider Name"
    
    async def fetch_costs(self, start_date, end_date):
        """Fetch costs from provider API"""
        # Implementation
        pass
    
    async def validate_credentials(self):
        """Validate API credentials"""
        # Implementation
        pass
    
    def get_models(self):
        """List available models"""
        # Implementation
        pass
    
    def get_model_info(self, model):
        """Get model details and pricing"""
        # Implementation
        pass
    
    async def estimate_cost(self, model, input_tokens, output_tokens):
        """Calculate cost"""
        # Implementation
        pass
```

---

## PART 5: DEPLOYMENT & VERSIONING

### Plugin Versioning

```python
# llmlab/plugins/manifest.json
{
  "id": "cohere-provider",
  "name": "Cohere Cost Provider",
  "version": "1.0.0",
  "author": "LLMLab Community",
  "description": "Cost tracking for Cohere API",
  "llmlab_version": ">=1.0.0",
  "type": "provider",
  "requirements": [
    "httpx>=0.24.0",
    "pydantic>=2.0.0"
  ]
}
```

### Plugin Installation

```bash
# From GitHub
llmlab install https://github.com/community/llmlab-cohere-provider

# From registry (future)
llmlab install cohere-provider
```

---

## PART 6: PLUGIN ECOSYSTEM ROADMAP

### Phase 1 (Q1 2024): Foundation
- [ ] Provider plugin system live
- [ ] 5 community providers
- [ ] Integration framework
- [ ] Documentation & examples

### Phase 2 (Q2 2024): Growth
- [ ] 20+ community providers
- [ ] Plugin registry (discoverable)
- [ ] Rating system
- [ ] Revenue sharing for creators

### Phase 3 (Q3 2024): Monetization
- [ ] Premium plugins
- [ ] Plugin marketplace
- [ ] Affiliate program
- [ ] Sponsor model

### Phase 4 (Q4 2024+): Scale
- [ ] 100+ plugins
- [ ] Multi-language SDK support
- [ ] Enterprise plugin support
- [ ] White-label solutions

---

## APPENDIX: PLUGIN EXAMPLES

### Example: Mistral AI Provider

```python
# llmlab/providers/mistral_provider.py

class MistralProvider(ProviderBase):
    PROVIDER_NAME = "mistral"
    DISPLAY_NAME = "Mistral AI"
    API_BASE = "https://api.mistral.ai/v1"
    
    MODELS = {
        "mistral-medium": {"input": 0.0007, "output": 0.0021},
        "mistral-small": {"input": 0.00014, "output": 0.00042},
        "mistral-tiny": {"input": 0.00014, "output": 0.00042},
    }
    
    # Implementation...
```

### Example: GitHub Actions Integration

```yaml
# .github/workflows/llmlab-evals.yml
name: LLMLab Evals

on: [pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: llmlab/github-action@v1
        with:
          api-key: ${{ secrets.LLMLAB_API_KEY }}
          project: my-project
          evals: |
            - pii_detection
            - hallucination_check
            - cost_comparison
```

---

## CONCLUSION

LLMLab's plugin system enables:
- ✅ Community-driven extensibility
- ✅ Easy onboarding of new providers
- ✅ Ecosystem growth
- ✅ Sustainable development model

**Get Started:** `CONTRIBUTING.md` has step-by-step instructions.
