"""
LLMLab Configuration Management
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def get_config_dir() -> Path:
    """Get LLMLab config directory"""
    config_dir = Path.home() / ".llmlab"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get LLMLab config file path"""
    return get_config_dir() / "config.json"


def get_config() -> Dict[str, Any]:
    """
    Load configuration from file.

    Returns:
        Config dict
    """
    config_file = get_config_file()
    if not config_file.exists():
        return {}

    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")
        return {}


def set_config(key: str, value: Any) -> None:
    """
    Set a configuration value.

    Args:
        key: Config key
        value: Config value
    """
    config = get_config()
    config[key] = value

    config_file = get_config_file()
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save config: {e}")


def delete_config(key: str) -> None:
    """
    Delete a configuration value.

    Args:
        key: Config key
    """
    config = get_config()
    if key in config:
        del config[key]

    config_file = get_config_file()
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save config: {e}")


def get_api_key() -> Optional[str]:
    """Get API key from config"""
    return get_config().get("api_key")


def set_api_key(api_key: str) -> None:
    """Set API key in config"""
    set_config("api_key", api_key)


def get_backend_url() -> str:
    """Get backend URL from config (defaults to localhost)"""
    return get_config().get("backend_url", "http://localhost:8000")


def set_backend_url(url: str) -> None:
    """Set backend URL in config"""
    set_config("backend_url", url)
