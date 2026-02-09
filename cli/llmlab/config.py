"""Configuration management for LLMLab CLI."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .security import encrypt_value, decrypt_value


CONFIG_DIR = Path.home() / ".llmlab"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir() -> None:
    """Ensure the config directory exists with proper permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.chmod(0o700)  # Only owner can access


def load_config() -> Dict[str, Any]:
    """Load configuration from disk."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to disk."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    CONFIG_FILE.chmod(0o600)  # Only owner can read/write


def get_token() -> Optional[str]:
    """Get the stored JWT token."""
    config = load_config()
    encrypted = config.get("token")
    if encrypted:
        return decrypt_value(encrypted)
    return None


def set_token(token: str) -> None:
    """Store JWT token (encrypted)."""
    config = load_config()
    config["token"] = encrypt_value(token)
    save_config(config)


def remove_token() -> None:
    """Remove stored JWT token."""
    config = load_config()
    config.pop("token", None)
    config.pop("user", None)
    save_config(config)


def get_user() -> Optional[Dict[str, Any]]:
    """Get stored user info."""
    config = load_config()
    return config.get("user")


def set_user(user: Dict[str, Any]) -> None:
    """Store user info."""
    config = load_config()
    config["user"] = user
    save_config(config)


def get_api_keys() -> Dict[str, str]:
    """Get all stored API keys (decrypted)."""
    config = load_config()
    encrypted_keys = config.get("api_keys", {})
    return {
        provider: decrypt_value(encrypted)
        for provider, encrypted in encrypted_keys.items()
    }


def set_api_key(provider: str, key: str) -> None:
    """Store an API key (encrypted)."""
    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][provider] = encrypt_value(key)
    save_config(config)


def get_api_key(provider: str) -> Optional[str]:
    """Get a specific API key (decrypted)."""
    keys = get_api_keys()
    return keys.get(provider)


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return get_token() is not None
