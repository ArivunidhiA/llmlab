"""Show cost optimization tips"""

import click

from llmlab.cli.utils import print_error, print_info, print_table
from llmlab.sdk.api_client import APIClient
from llmlab.sdk.config import get_api_key


@click.command("optimize")
def optimize_cmd() -> None:
    """
    Show cost optimization recommendations.

    Analyzes your usage patterns and suggests ways to reduce costs.
    """
    api_key = get_api_key()
    if not api_key:
        print_error("API key not configured. Run 'llmlab init' first.")
        raise click.Abort()

    try:
        client = APIClient()
        tips = client.get_optimization_tips()
    except Exception as e:
        print_error(f"Failed to fetch optimization tips: {e}")
        raise click.Abort()

    click.echo(click.style("\n💡 Cost Optimization Tips\n", fg="cyan", bold=True))

    # Display tips
    if "tips" in tips:
        for i, tip in enumerate(tips["tips"], 1):
            title = tip.get("title", "Tip")
            description = tip.get("description", "")
            savings = tip.get("potential_savings", 0)

            click.echo(f"{i}. {click.style(title, fg='yellow', bold=True)}")
            click.echo(f"   {description}")
            if savings > 0:
                click.echo(
                    f"   {click.style(f'Potential savings: ${savings:.2f}/month', fg='green')}"
                )
            click.echo()

    # Display summary
    if "total_potential_savings" in tips:
        total = tips["total_potential_savings"]
        click.echo(
            click.style(
                f"Total potential monthly savings: ${total:.2f}",
                fg="green",
                bold=True,
            )
        )
        click.echo()

    # Display model recommendations
    if "model_recommendations" in tips:
        headers = ["Current Model", "Recommended Model", "Savings/Month"]
        rows = [
            [
                rec.get("current_model"),
                rec.get("recommended_model"),
                f"${rec.get('savings', 0):.2f}",
            ]
            for rec in tips.get("model_recommendations", [])
        ]
        if rows:
            print_table(headers, rows, "Model Optimization")

    click.echo()
