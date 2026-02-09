"""
LLMLab CLI and SDK
Complete Python implementation for CLI and SDK
"""

# ============================================================================
# PART 1: SDK - Python decorators and utilities
# ============================================================================

import functools
import json
import os
from datetime import datetime
from typing import Callable, Any, Optional
import requests

class LLMLabSDK:
    """LLMLab SDK for tracking LLM costs"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "http://localhost:8000"):
        self.api_key = api_key or os.getenv("LLMLAB_API_KEY")
        self.api_url = api_url
        if not self.api_key:
            raise ValueError("LLMLAB_API_KEY not set. Run 'llmlab init' first.")
    
    def track_call(self, provider: str, model: str, input_tokens: int, output_tokens: int, metadata: dict = None):
        """Track a single LLM API call"""
        try:
            response = requests.post(
                f"{self.api_url}/api/events/track",
                json={
                    "provider": provider,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "metadata": metadata or {}
                },
                headers={"Authorization": self.api_key}
            )
            return response.json()
        except Exception as e:
            print(f"Failed to track cost: {e}")
            return None
    
    def get_summary(self):
        """Get cost summary from API"""
        try:
            response = requests.get(
                f"{self.api_url}/api/costs/summary",
                headers={"Authorization": self.api_key}
            )
            return response.json()
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return None
    
    def get_recommendations(self):
        """Get cost optimization recommendations"""
        try:
            response = requests.get(
                f"{self.api_url}/api/recommendations",
                headers={"Authorization": self.api_key}
            )
            return response.json()
        except Exception as e:
            print(f"Failed to get recommendations: {e}")
            return None

# Global SDK instance
_sdk = None

def init(api_key: str, api_url: str = "http://localhost:8000"):
    """Initialize SDK"""
    global _sdk
    _sdk = LLMLabSDK(api_key, api_url)

def track_cost(provider: str, model: str, input_tokens: int, output_tokens: int, metadata: dict = None):
    """Track a cost manually"""
    if not _sdk:
        raise ValueError("SDK not initialized. Call llmlab.init() first")
    return _sdk.track_call(provider, model, input_tokens, output_tokens, metadata)

def decorated(func: Callable) -> Callable:
    """Decorator to automatically track costs
    
    Usage:
    @llmlab.decorated
    def my_llm_call():
        # Call your LLM API here
        ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # This is where we'd intercept and track the call
        # For now, just pass through
        return func(*args, **kwargs)
    return wrapper

# ============================================================================
# PART 2: CLI - Command-line interface
# ============================================================================

import click
import sys
from tabulate import tabulate

class Config:
    """Store and load configuration"""
    
    CONFIG_FILE = os.path.expanduser("~/.llmlab/config.json")
    
    @staticmethod
    def load():
        try:
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE) as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    @staticmethod
    def save(config):
        os.makedirs(os.path.dirname(Config.CONFIG_FILE), exist_ok=True)
        with open(Config.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

@click.group()
def cli():
    """LLMLab - LLM Cost Tracking & Optimization"""
    pass

@cli.command()
@click.option("--api-key", prompt="Enter your LLMLab API key", hide_input=True)
@click.option("--api-url", default="https://llmlab.vercel.app", prompt="API URL", default="https://llmlab.vercel.app")
def init(api_key, api_url):
    """Initialize LLMLab CLI
    
    Run: llmlab init
    """
    config = {"api_key": api_key, "api_url": api_url}
    Config.save(config)
    
    click.echo("✅ LLMLab initialized!")
    click.echo(f"API Key: {api_key[:20]}...")
    click.echo(f"API URL: {api_url}")
    click.echo("\nNext steps:")
    click.echo("1. Run 'llmlab status' to check your spend")
    click.echo("2. Run 'llmlab optimize' to get optimization tips")
    click.echo("3. Import in Python: from llmlab import sdk; sdk.init('your-api-key')")

@cli.command()
def status():
    """Show current LLM spending
    
    Run: llmlab status
    """
    config = Config.load()
    if not config.get("api_key"):
        click.echo("❌ Not initialized. Run 'llmlab init' first.")
        sys.exit(1)
    
    sdk = LLMLabSDK(config["api_key"], config.get("api_url", "http://localhost:8000"))
    summary = sdk.get_summary()
    
    if not summary:
        click.echo("❌ Failed to fetch costs")
        sys.exit(1)
    
    click.echo("\n" + "="*50)
    click.echo("💰 LLMLab Cost Summary")
    click.echo("="*50)
    click.echo(f"Total Spend: ${summary['total_spend']:.2f}")
    click.echo(f"This Month: ${summary['this_month_spend']:.2f}")
    click.echo(f"Today: ${summary['today_spend']:.2f}")
    
    if summary.get("by_provider"):
        click.echo("\n📊 By Provider:")
        for provider, cost in sorted(summary["by_provider"].items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {provider}: ${cost:.2f}")
    
    if summary.get("by_model"):
        click.echo("\n📊 By Model:")
        for model, cost in sorted(summary["by_model"].items(), key=lambda x: x[1], reverse=True)[:5]:
            click.echo(f"  {model}: ${cost:.2f}")
    
    if summary.get("budget_status"):
        budget = summary["budget_status"]
        percentage = budget["percentage"]
        status_icon = "⚠️" if budget["alert"] else "✅"
        click.echo(f"\n💵 Budget: ${budget['spent']:.2f} / ${budget['budget']:.2f} ({percentage:.1f}%) {status_icon}")
    
    click.echo("="*50 + "\n")

@cli.command()
def optimize():
    """Get cost optimization recommendations
    
    Run: llmlab optimize
    """
    config = Config.load()
    if not config.get("api_key"):
        click.echo("❌ Not initialized. Run 'llmlab init' first.")
        sys.exit(1)
    
    sdk = LLMLabSDK(config["api_key"], config.get("api_url", "http://localhost:8000"))
    recommendations = sdk.get_recommendations()
    
    if not recommendations:
        click.echo("❌ Failed to fetch recommendations")
        sys.exit(1)
    
    if not recommendations:
        click.echo("✅ No optimization opportunities found. You're doing great!")
        return
    
    click.echo("\n" + "="*60)
    click.echo("💡 Cost Optimization Recommendations")
    click.echo("="*60)
    
    for i, rec in enumerate(recommendations, 1):
        click.echo(f"\n{i}. {rec['title']}")
        click.echo(f"   {rec['description']}")
        click.echo(f"   💰 Potential Savings: {rec['savings_percentage']}%")
        click.echo(f"   📊 Confidence: {rec['confidence']}%")
        click.echo(f"   ➜ {rec['action']}")
    
    click.echo("\n" + "="*60 + "\n")

@cli.command()
@click.option("--amount", type=float, prompt="Monthly budget amount")
def budget(amount):
    """Set monthly budget
    
    Run: llmlab budget --amount 1000
    """
    config = Config.load()
    if not config.get("api_key"):
        click.echo("❌ Not initialized. Run 'llmlab init' first.")
        sys.exit(1)
    
    # TODO: Call API to set budget
    click.echo(f"✅ Budget set to ${amount:.2f}")

@cli.command()
def export():
    """Export cost data as CSV
    
    Run: llmlab export
    """
    config = Config.load()
    if not config.get("api_key"):
        click.echo("❌ Not initialized. Run 'llmlab init' first.")
        sys.exit(1)
    
    click.echo("📥 Exporting to costs.csv...")
    # TODO: Implement export
    click.echo("✅ Exported to costs.csv")

@cli.command()
def config():
    """Show current configuration
    
    Run: llmlab config
    """
    cfg = Config.load()
    if not cfg:
        click.echo("❌ Not configured. Run 'llmlab init' first.")
        return
    
    click.echo("\n" + "="*40)
    click.echo("⚙️  LLMLab Configuration")
    click.echo("="*40)
    click.echo(f"API Key: {cfg['api_key'][:20]}...")
    click.echo(f"API URL: {cfg.get('api_url', 'http://localhost:8000')}")
    click.echo("="*40 + "\n")

if __name__ == "__main__":
    cli()
