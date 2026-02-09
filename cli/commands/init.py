"""Initialize LLMLab project"""

import click

from llmlab.sdk.config import get_config, get_config_file, set_api_key, set_backend_url


@click.command("init")
@click.option("--api-key", prompt=False, help="LLMLab API key")
@click.option("--backend-url", default="http://localhost:8000", help="Backend URL")
def init_cmd(api_key: str, backend_url: str) -> None:
    """
    Initialize LLMLab project.

    Sets up API key and backend configuration.
    """
    click.echo(click.style("\n🚀 LLMLab Initialization\n", fg="cyan", bold=True))

    # If no API key provided, prompt for it
    if not api_key:
        api_key = click.prompt("Enter your LLMLab API key", hide_input=True)

    # Confirm backend URL
    if click.confirm(f"Use backend URL: {backend_url}?"):
        set_backend_url(backend_url)
    else:
        custom_url = click.prompt("Enter custom backend URL")
        set_backend_url(custom_url)

    # Set API key
    set_api_key(api_key)

    config_file = get_config_file()
    click.echo(
        click.style(
            f"\n✓ Configuration saved to {config_file}\n",
            fg="green",
        )
    )

    # Show current config
    config = get_config()
    click.echo(click.style("Current Configuration:", fg="cyan", bold=True))
    click.echo(f"  Backend URL: {config.get('backend_url')}")
    click.echo(f"  API Key: {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'Not set'}\n")

    click.echo(click.style("Next steps:", fg="blue", bold=True))
    click.echo("  • Use @track_cost decorator in your code")
    click.echo("  • Or use 'with llmlab.track():' context manager")
    click.echo("  • Run 'llmlab status' to check your spending\n")
