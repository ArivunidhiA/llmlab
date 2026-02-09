"""Set monthly budget"""

import click

from llmlab.cli.utils import format_currency, print_error, print_success
from llmlab.sdk.api_client import APIClient
from llmlab.sdk.config import get_api_key


@click.command("budget")
@click.argument("amount", type=float, required=False)
def budget_cmd(amount: float) -> None:
    """
    Set or view monthly budget.

    Usage:
        llmlab budget           # View current budget
        llmlab budget 100       # Set budget to $100
    """
    api_key = get_api_key()
    if not api_key:
        print_error("API key not configured. Run 'llmlab init' first.")
        raise click.Abort()

    try:
        client = APIClient()

        if amount is None:
            # View current budget
            status = client.get_status()
            budget = status.get("budget", 0)
            spend = status.get("current_spend", 0)

            click.echo(click.style("\n💰 Monthly Budget\n", fg="cyan", bold=True))
            click.echo(f"  Budget:        {format_currency(budget)}")
            click.echo(f"  Current Spend: {format_currency(spend)}")
            click.echo(f"  Remaining:     {format_currency(max(0, budget - spend))}")
            click.echo()
        else:
            # Set budget
            client.set_budget(amount)
            print_success(f"Budget set to {format_currency(amount)}")
            click.echo()

    except Exception as e:
        print_error(f"Failed to update budget: {e}")
        raise click.Abort()
