"""Stats command - View usage and cost statistics."""

from datetime import datetime
from typing import Dict, List, Any

import click

from ..config import is_authenticated
from ..api import get_stats, APIError, AuthenticationError, NetworkError


def format_cost(cost: float) -> str:
    """Format cost as currency."""
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


def format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}"


def print_table(data: List[Dict[str, Any]], show_daily: bool = False):
    """Print a formatted table of stats."""
    if not data:
        click.echo(click.style("No usage data for this period.", fg="yellow"))
        return
    
    # Calculate column widths
    model_width = max(len(row.get("model", "")) for row in data)
    model_width = max(model_width, len("Model"))
    
    # Header
    header = f"{'Model':<{model_width}}  {'Cost':>10}  {'Calls':>8}  {'Tokens':>12}"
    click.echo(click.style(header, fg="bright_white", bold=True))
    click.echo("─" * len(header))
    
    total_cost = 0
    total_calls = 0
    total_tokens = 0
    
    for row in data:
        model = row.get("model", "unknown")
        cost = row.get("cost", 0)
        calls = row.get("calls", 0)
        tokens = row.get("tokens", 0)
        
        total_cost += cost
        total_calls += calls
        total_tokens += tokens
        
        line = f"{model:<{model_width}}  {format_cost(cost):>10}  {format_number(calls):>8}  {format_number(tokens):>12}"
        click.echo(line)
    
    # Total row
    click.echo("─" * len(header))
    total_line = f"{'TOTAL':<{model_width}}  {format_cost(total_cost):>10}  {format_number(total_calls):>8}  {format_number(total_tokens):>12}"
    click.echo(click.style(total_line, fg="green", bold=True))


def print_daily_breakdown(data: List[Dict[str, Any]]):
    """Print daily breakdown if available."""
    if not data:
        return
    
    click.echo()
    click.echo(click.style("Daily Breakdown", fg="bright_white", bold=True))
    click.echo("─" * 40)
    
    for day in data:
        date = day.get("date", "")
        cost = day.get("cost", 0)
        calls = day.get("calls", 0)
        
        # Format date nicely
        try:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            date_str = dt.strftime("%a %b %d")
        except:
            date_str = date[:10]
        
        line = f"{date_str:<12}  {format_cost(cost):>10}  {format_number(calls):>6} calls"
        click.echo(line)


@click.command()
@click.option("--today", "period", flag_value="today", help="Show today's stats only")
@click.option("--week", "period", flag_value="week", help="Show this week's stats")
@click.option("--month", "period", flag_value="month", default=True, help="Show this month's stats (default)")
@click.option("--all", "period", flag_value="all", help="Show all-time stats")
@click.option("--daily", "-d", is_flag=True, help="Include daily breakdown")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def stats(period: str, daily: bool, as_json: bool):
    """View your usage and cost statistics.
    
    Track spending across all LLM providers in one place.
    
    \b
    Examples:
      llmlab stats              # This month's stats
      llmlab stats --today      # Today only
      llmlab stats --week -d    # This week with daily breakdown
    """
    if not is_authenticated():
        click.echo(click.style("✗ Not logged in.", fg="red"))
        click.echo("  Run 'llmlab login' first.")
        raise click.Abort()
    
    period = period or "month"
    
    try:
        with click.progressbar(length=1, label="Fetching stats", 
                              show_eta=False, show_percent=False) as bar:
            result = get_stats(period)
            bar.update(1)
        
        click.echo()
        
        # JSON output
        if as_json:
            import json
            click.echo(json.dumps(result, indent=2))
            return
        
        # Period header
        period_labels = {
            "today": "Today",
            "week": "This Week",
            "month": "This Month",
            "all": "All Time",
        }
        label = period_labels.get(period, period.title())
        click.echo(click.style(f"📊 Usage Stats - {label}", fg="cyan", bold=True))
        click.echo()
        
        # Main table
        by_model = result.get("by_model", [])
        print_table(by_model)
        
        # Daily breakdown
        if daily:
            daily_data = result.get("daily", [])
            print_daily_breakdown(daily_data)
        
        click.echo()
    
    except AuthenticationError as e:
        click.echo(click.style(f"✗ {e.message}", fg="red"))
        raise click.Abort()
    except NetworkError as e:
        click.echo(click.style(f"✗ {e.message}", fg="red"))
        raise click.Abort()
    except APIError as e:
        click.echo(click.style(f"✗ {e.message}", fg="red"))
        raise click.Abort()
