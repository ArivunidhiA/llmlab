"""Manage configuration"""

import click

from llmlab.cli.utils import format_table_from_dict, print_error, print_success
from llmlab.sdk.config import (
    delete_config,
    get_backend_url,
    get_config,
    get_config_file,
    set_api_key,
    set_backend_url,
)


@click.command("config")
@click.option("--set", "set_option", nargs=2, help="Set a config value", type=(str, str))
@click.option("--get", "get_option", help="Get a config value")
@click.option("--list", "list_config", is_flag=True, help="List all config values")
@click.option("--reset", is_flag=True, help="Reset configuration")
def config_cmd(
    set_option: tuple, get_option: str, list_config: bool, reset: bool
) -> None:
    """
    Manage LLMLab configuration.

    Usage:
        llmlab config --list                          # Show all settings
        llmlab config --get api_key                   # Get specific setting
        llmlab config --set api_key YOUR_KEY          # Set a value
        llmlab config --reset                         # Reset all settings
    """
    config_file = get_config_file()

    if list_config:
        # List all config
        config = get_config()
        click.echo(click.style(f"\n📋 Configuration ({config_file})\n", fg="cyan", bold=True))

        display_config = {
            "backend_url": config.get("backend_url", "Not set"),
            "api_key": (
                "***" + config.get("api_key", "")[-4:]
                if config.get("api_key")
                else "Not set"
            ),
        }
        format_table_from_dict(display_config)

    elif get_option:
        # Get specific value
        config = get_config()
        value = config.get(get_option, "Not found")
        if get_option == "api_key" and isinstance(value, str) and value != "Not found":
            value = "***" + value[-4:]
        click.echo(f"{get_option}: {value}")

    elif set_option:
        # Set value
        key, value = set_option
        if key == "api_key":
            set_api_key(value)
        elif key == "backend_url":
            set_backend_url(value)
        else:
            from llmlab.sdk.config import set_config

            set_config(key, value)
        print_success(f"Set {key} = {value if key != 'api_key' else '***' + value[-4:]}")

    elif reset:
        # Reset config
        if click.confirm("This will delete all configuration. Continue?"):
            try:
                config_file.unlink()
                print_success("Configuration reset")
            except Exception as e:
                print_error(f"Failed to reset configuration: {e}")

    else:
        # No options provided
        click.echo(click.style("Configuration Manager\n", fg="cyan", bold=True))
        click.echo("Use --list to show all settings")
        click.echo("Use --get <key> to get a value")
        click.echo("Use --set <key> <value> to set a value")
        click.echo("Use --reset to clear all settings")
        click.echo()
