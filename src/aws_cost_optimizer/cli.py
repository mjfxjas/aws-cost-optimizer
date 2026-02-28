"""CLI for AWS Cost Optimizer"""
from __future__ import annotations

import sys
from typing import Dict, List

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from . import analyzers

console = Console()
SERVICES = ["all", "dynamodb", "lambda", "s3", "cloudfront"]


def _collect_recommendations(service: str) -> List[Dict]:
    recommendations: List[Dict] = []
    if service in ["all", "dynamodb"]:
        recommendations.extend(analyzers.analyze_dynamodb())
    if service in ["all", "lambda"]:
        recommendations.extend(analyzers.analyze_lambda())
    if service in ["all", "s3"]:
        recommendations.extend(analyzers.analyze_s3())
    if service in ["all", "cloudfront"]:
        recommendations.extend(analyzers.analyze_cloudfront())
    return recommendations


def _render_recommendations(recommendations: List[Dict]) -> None:
    if not recommendations:
        console.print("[green]No cost optimization opportunities found![/green]")
        return

    table = Table(title="Cost Optimization Recommendations")
    table.add_column("Service", style="cyan")
    table.add_column("Resource", style="yellow")
    table.add_column("Issue", style="red")
    table.add_column("Savings", style="green")
    table.add_column("Action", style="blue")

    for rec in recommendations:
        table.add_row(
            rec["service"],
            rec["resource"],
            rec["issue"],
            rec["savings"],
            rec["action"],
        )

    console.print(table)
    console.print(f"\n[bold]Total recommendations: {len(recommendations)}[/bold]")


def _apply_recommendation(rec: Dict, dry_run: bool) -> None:
    service = rec["service"].lower()
    resource = rec["resource"]
    if dry_run:
        console.print(f"[yellow]DRY RUN: Would optimize {service}/{resource}[/yellow]")
        return

    # NOTE: Mutating API calls are intentionally not wired yet for safety.
    # This keeps apply/apply-all explicit and reviewable.
    console.print(
        f"[yellow]Planned optimize step for {service}/{resource}[/yellow]"
        " [dim](execution engine not implemented yet)[/dim]"
    )


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx: click.Context):
    """AWS Cost Optimizer - Find and fix cost inefficiencies"""
    if ctx.invoked_subcommand is None:
        # Default to menu for interactive shells; help for non-interactive usage.
        if sys.stdin.isatty():
            ctx.invoke(menu)
        else:
            click.echo(ctx.get_help())


@main.command()
@click.option("--service", type=click.Choice(SERVICES), default="all")
def analyze(service: str):
    """Analyze AWS resources for cost optimization opportunities"""
    console.print(f"[bold cyan]Analyzing {service} for cost optimization...[/bold cyan]\n")
    _render_recommendations(_collect_recommendations(service))


@main.command()
@click.option("--service", type=click.Choice(SERVICES), default="all", help="Service scope")
@click.argument("resource", required=False)
@click.option("--all", "apply_all", is_flag=True, help="Apply to all recommendations in scope")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt for bulk apply")
def apply(service: str, resource: str | None, apply_all: bool, dry_run: bool, yes: bool):
    """Apply cost optimization to one resource or all recommendations."""
    if apply_all:
        recs = _collect_recommendations(service)
        if not recs:
            console.print("[green]Nothing to apply.[/green]")
            return

        console.print(f"[bold cyan]Applying {len(recs)} recommendation(s) in scope: {service}[/bold cyan]")
        if not dry_run and not yes:
            confirmed = Confirm.ask("Proceed with apply-all?", default=False)
            if not confirmed:
                console.print("[yellow]Canceled.[/yellow]")
                return

        for rec in recs:
            _apply_recommendation(rec, dry_run=dry_run)
        console.print("[green]Apply-all run complete.[/green]")
        return

    if not resource:
        raise click.UsageError(
            "For single-resource apply, pass RESOURCE. "
            "Example: aws-cost-optimizer apply --service dynamodb my-table --dry-run\n"
            "Or use --all for bulk mode."
        )

    if service == "all":
        raise click.UsageError("Single-resource apply requires a specific --service (not 'all').")

    _apply_recommendation({"service": service, "resource": resource}, dry_run=dry_run)
    if not dry_run:
        console.print("[green]Optimization step queued.[/green]")


@main.command()
def report():
    """Generate cost optimization report"""
    console.print("[bold cyan]Cost Optimization Report[/bold cyan]\n")
    console.print("Feature coming soon!")


@main.command()
def menu():
    """Launch interactive hub menu (WonderDash-style flow)."""
    if not sys.stdin.isatty():
        console.print("[red]Interactive menu requires a terminal (TTY).[/red]")
        return

    while True:
        console.print(
            Panel(
                "[bold cyan]AWS Cost Optimizer Hub[/bold cyan]\n"
                "[1] Analyze all services\n"
                "[2] Analyze one service\n"
                "[3] Apply all (dry-run)\n"
                "[4] Apply one resource\n"
                "[5] Report\n"
                "[0] Exit",
                border_style="cyan",
            )
        )

        choice = IntPrompt.ask("Select", default=1)
        if choice == 0:
            console.print("[cyan]Bye.[/cyan]")
            return
        if choice == 1:
            _render_recommendations(_collect_recommendations("all"))
        elif choice == 2:
            service = Prompt.ask("Service", choices=SERVICES[1:], default="dynamodb")
            _render_recommendations(_collect_recommendations(service))
        elif choice == 3:
            service = Prompt.ask("Scope", choices=SERVICES, default="all")
            recs = _collect_recommendations(service)
            if not recs:
                console.print("[green]Nothing to apply.[/green]")
                continue
            console.print(f"[bold]Running dry-run apply-all for {len(recs)} recommendation(s)...[/bold]")
            for rec in recs:
                _apply_recommendation(rec, dry_run=True)
        elif choice == 4:
            service = Prompt.ask("Service", choices=SERVICES[1:], default="dynamodb")
            resource = Prompt.ask("Resource")
            _apply_recommendation({"service": service, "resource": resource}, dry_run=True)
        elif choice == 5:
            report()
        else:
            console.print("[red]Invalid choice.[/red]")


if __name__ == "__main__":
    main()
