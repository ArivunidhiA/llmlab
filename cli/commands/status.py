"""Show current spending status"""

import click

from llmlab.cli.utils import (
    format_currency,
    format_percentage,
    format_table_from_dict,
    print_error,
    print_info,
    print_table,
)
from llmlab.sdk.api_client import APIClient
from llmlab.sdk.config import get_api_key


@click.command("status")
def status_cmd() -> None:
    """
    Show current month's spending and budget status.

    Displays total spend, budget usage, and breakdown by model.
    """
    api_key = get_api_key()
    if not api_key:
        print_error("API key not configured. Run 'llmlab init' first.")
        raise click.Abort()

    try:
        client = APIClient()
        status_data = client.get_status()
    except Exception as e:
        print_error(f"Failed to fetch status: {e}")
        raise click.Abort()

    # Display main status
    click.echo(click.style("\n📊 LLMLab Status\n", fg="cyan", bold=True))

    spend = status_data.get("current_spend", 0)
    budget = status_data.get("budget", 0)
    percent_used = (spend / budget * 100) if budget > 0 else 0

    # Main metrics
    metrics = {
        "Current Spend": format_currency(spend),
        "Monthly Budget": format_currency(budget) if budget > 0 else "Not set",
        "Budget Used": format_percentage(percent_used) if budget > 0 else "—",
        "Remaining": format_currency(budget - spend) if budget > 0 else "—",
    }
    format_table_from_dict(metrics, "Current Month")

    # Breakdown by model
    models = status_data.get("by_model", {})
    if models:
        headers = ["Model", "Cost", "Tokens", "Calls"]
        rows = [
            [
                model,
                format_currency(data.get("cost", 0)),
                data.get("tokens", 0),
                data.get("calls", 0),
            ]
            for model, data in sorted(
                models.items(), key=lambda x: x[1].get("cost", 0), reverse=True
            )
        ]
        print_table(headers, rows, "Cost Breakdown by Model")

    # Warnings
    if percent_used > 80:
        print_info(f"⚠️  You've used {percent_used:.0f}% of your monthly budget!")

    click.echo()
