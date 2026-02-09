"""Configure command - Add and manage API keys."""

import click

from ..config import set_api_key, get_api_keys, is_authenticated
from ..security import mask_key
from ..api import store_provider_key, APIError, NetworkError


# Supported providers
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "key_prefix": "sk-",
        "example": "sk-...",
    },
    "anthropic": {
        "name": "Anthropic",
        "key_prefix": "sk-ant-",
        "example": "sk-ant-...",
    },
    "google": {
        "name": "Google (Gemini)",
        "key_prefix": "",
        "example": "AIza...",
    },
    "mistral": {
        "name": "Mistral",
        "key_prefix": "",
        "example": "",
    },
    "cohere": {
        "name": "Cohere",
        "key_prefix": "",
        "example": "",
    },
}


def validate_key(provider: str, key: str) -> bool:
    """Basic validation of API key format."""
    if not key or len(key) < 10:
        return False
    
    info = PROVIDERS.get(provider, {})
    prefix = info.get("key_prefix", "")
    
    if prefix and not key.startswith(prefix):
        return False
    
    return True


@click.command()
@click.option("--provider", "-p", type=click.Choice(list(PROVIDERS.keys())), 
              help="Configure a specific provider only")
@click.option("--list", "-l", "list_keys", is_flag=True, help="List configured providers")
@click.option("--sync", "-s", is_flag=True, help="Sync keys to backend (requires login)")
def configure(provider: str, list_keys: bool, sync: bool):
    """Configure API keys for LLM providers.
    
    Your keys are encrypted and stored locally in ~/.llmlab/config.json.
    Use --sync to also store them on the backend for web access.
    
    \b
    Supported providers:
      - openai      OpenAI (GPT-4, GPT-3.5)
      - anthropic   Anthropic (Claude)
      - google      Google (Gemini)
      - mistral     Mistral AI
      - cohere      Cohere
    """
    # List configured keys
    if list_keys:
        keys = get_api_keys()
        if not keys:
            click.echo(click.style("No API keys configured.", fg="yellow"))
            click.echo("Run 'llmlab configure' to add keys.")
            return
        
        click.echo("Configured providers:\n")
        for p, key in keys.items():
            name = PROVIDERS.get(p, {}).get("name", p)
            masked = mask_key(key)
            click.echo(f"  {name:20} {masked}")
        click.echo()
        return
    
    # Configure specific provider or all
    providers_to_configure = [provider] if provider else list(PROVIDERS.keys())
    
    click.echo("Configure your API keys")
    click.echo(click.style("Keys are encrypted and stored locally.\n", fg="bright_black"))
    
    configured = []
    skipped = []
    
    for p in providers_to_configure:
        info = PROVIDERS[p]
        name = info["name"]
        example = info.get("example", "")
        
        # Check if already configured
        existing = get_api_keys().get(p)
        if existing:
            existing_hint = f" [{mask_key(existing)}]"
        else:
            existing_hint = ""
        
        # Prompt for key
        prompt = f"{name} API key{existing_hint}"
        if example:
            prompt += f" ({example})"
        
        key = click.prompt(
            prompt,
            default="",
            show_default=False,
            hide_input=True,
        )
        
        if not key:
            if existing:
                skipped.append(name)
            continue
        
        # Validate
        if not validate_key(p, key):
            click.echo(click.style(f"  Invalid key format for {name}", fg="yellow"))
            continue
        
        # Store locally
        set_api_key(p, key)
        configured.append(name)
        
        # Optionally sync to backend
        if sync and is_authenticated():
            try:
                store_provider_key(p, key)
                click.echo(click.style(f"  ✓ {name} synced to backend", fg="green"))
            except (APIError, NetworkError) as e:
                click.echo(click.style(f"  ✗ Failed to sync {name}: {e.message}", fg="red"))
    
    # Summary
    click.echo()
    if configured:
        click.echo(click.style(f"✓ Keys stored securely: {', '.join(configured)}", fg="green"))
    if skipped:
        click.echo(click.style(f"  Kept existing: {', '.join(skipped)}", fg="bright_black"))
    
    if not configured and not skipped:
        click.echo(click.style("No keys configured.", fg="yellow"))
    else:
        click.echo()
        click.echo("Next: Run 'llmlab proxy-key' to get your unified API key.")
