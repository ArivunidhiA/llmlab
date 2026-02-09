"""Logout command - Remove stored credentials."""

import click

from ..config import remove_token, is_authenticated, get_user


@click.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def logout(yes: bool):
    """Log out and remove stored credentials.
    
    This removes your JWT token and user info from local storage.
    Your API keys will be preserved.
    """
    if not is_authenticated():
        click.echo(click.style("Not logged in.", fg="yellow"))
        return
    
    user = get_user()
    username = user.get("username", "user") if user else "user"
    
    if not yes:
        click.confirm(
            f"Log out as {username}?",
            abort=True,
        )
    
    remove_token()
    
    click.echo()
    click.echo(click.style("✓ Successfully logged out", fg="green"))
    click.echo("  Your API keys are still stored locally.")
    click.echo("  Run 'llmlab login' to authenticate again.")
