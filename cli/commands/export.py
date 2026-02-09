"""Export costs to CSV"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from llmlab.cli.utils import print_error, print_success
from llmlab.sdk.api_client import APIClient
from llmlab.sdk.config import get_api_key


@click.command("export")
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", help="End date (YYYY-MM-DD)")
@click.option("--output", "-o", help="Output CSV file path", default=None)
def export_cmd(start_date: Optional[str], end_date: Optional[str], output: Optional[str]) -> None:
    """
    Export costs to CSV.

    Usage:
        llmlab export                                  # Export this month
        llmlab export --start-date 2024-01-01          # Export from Jan 1
        llmlab export -o costs.csv                     # Save to specific file
    """
    api_key = get_api_key()
    if not api_key:
        print_error("API key not configured. Run 'llmlab init' first.")
        raise click.Abort()

    try:
        client = APIClient()
        costs_data = client.get_costs(start_date=start_date, end_date=end_date)
    except Exception as e:
        print_error(f"Failed to fetch costs: {e}")
        raise click.Abort()

    # Determine output file
    if not output:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output = f"llmlab_costs_{now}.csv"

    output_path = Path(output)

    # Extract costs
    costs = costs_data.get("costs", [])
    if not costs:
        click.echo("No costs found for the specified period.")
        return

    # Write CSV
    try:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "timestamp",
                    "model",
                    "provider",
                    "tokens",
                    "cost",
                    "metadata",
                ],
            )
            writer.writeheader()
            for cost in costs:
                writer.writerow(
                    {
                        "timestamp": cost.get("timestamp", ""),
                        "model": cost.get("model", ""),
                        "provider": cost.get("provider", ""),
                        "tokens": cost.get("tokens", 0),
                        "cost": cost.get("cost", 0),
                        "metadata": cost.get("metadata", {}),
                    }
                )

        print_success(f"Exported {len(costs)} costs to {output_path}")
        click.echo()

    except Exception as e:
        print_error(f"Failed to write CSV: {e}")
        raise click.Abort()
