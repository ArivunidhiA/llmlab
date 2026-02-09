"""
CLI Utility functions
"""

from typing import Any, Dict, List

import click
from tabulate import tabulate


def print_table(headers: List[str], rows: List[List[Any]], title: Optional[str] = None) -> None:
    """
    Print a formatted table.

    Args:
        headers: Column headers
        rows: Table rows
        title: Optional table title
    """
    if title:
        click.echo(click.style(f"\n{title}\n", fg="cyan", bold=True))

    table_str = tabulate(rows, headers=headers, tablefmt="grid")
    click.echo(table_str)
    click.echo()


def print_success(message: str) -> None:
    """Print success message"""
    click.echo(click.style(f"✓ {message}", fg="green"))


def print_error(message: str) -> None:
    """Print error message"""
    click.echo(click.style(f"✗ {message}", fg="red"), err=True)


def print_warning(message: str) -> None:
    """Print warning message"""
    click.echo(click.style(f"⚠ {message}", fg="yellow"))


def print_info(message: str) -> None:
    """Print info message"""
    click.echo(click.style(f"ℹ {message}", fg="blue"))


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return click.style(f"${amount:.4f}", fg="cyan", bold=True)


def format_percentage(value: float) -> str:
    """Format percentage with color"""
    if value > 80:
        color = "red"
    elif value > 50:
        color = "yellow"
    else:
        color = "green"
    return click.style(f"{value:.1f}%", fg=color)


def format_table_from_dict(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """Format and print a dict as a table"""
    if title:
        click.echo(click.style(f"\n{title}\n", fg="cyan", bold=True))

    for key, value in data.items():
        if isinstance(value, float) and "cost" in key.lower():
            value = format_currency(value)
        click.echo(f"  {key}: {value}")
    click.echo()
