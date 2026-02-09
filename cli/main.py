"""
LLMLab CLI - Main entry point
"""

import sys
from typing import Optional

import click

from llmlab.cli.commands import budget, config, export, init, optimize, status


@click.group()
@click.version_option()
def cli() -> None:
    """
    LLMLab - Cost tracking and optimization for LLM applications

    Track, monitor, and optimize costs for your LLM API calls.
    """
    pass


# Register commands
cli.add_command(init.init_cmd)
cli.add_command(status.status_cmd)
cli.add_command(budget.budget_cmd)
cli.add_command(optimize.optimize_cmd)
cli.add_command(export.export_cmd)
cli.add_command(config.config_cmd)


def main() -> None:
    """Entry point for CLI"""
    try:
        cli()
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
