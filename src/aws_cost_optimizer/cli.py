"""CLI for AWS Cost Optimizer"""
from __future__ import annotations

import sys
from typing import Dict, List

import boto3
import click
from botocore.exceptions import ClientError
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


def _apply_dynamodb(resource: str, settings: Dict) -> tuple[bool, str]:
    client = boto3.client("dynamodb")
    table = client.describe_table(TableName=resource)["Table"]
    billing_mode = table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
    if billing_mode == "PROVISIONED":
        return True, "Already provisioned; skipped"

    client.update_table(
        TableName=resource,
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": settings["dynamodb_rcu"],
            "WriteCapacityUnits": settings["dynamodb_wcu"],
        },
    )
    return True, f"Switched to PROVISIONED ({settings['dynamodb_rcu']} RCU / {settings['dynamodb_wcu']} WCU)"


def _apply_lambda(resource: str, settings: Dict) -> tuple[bool, str]:
    client = boto3.client("lambda")
    client.put_function_concurrency(
        FunctionName=resource,
        ReservedConcurrentExecutions=settings["lambda_concurrency"],
    )
    return True, f"Set reserved concurrency to {settings['lambda_concurrency']}"


def _apply_s3(resource: str, settings: Dict) -> tuple[bool, str]:
    client = boto3.client("s3")
    expire_days = settings["s3_expire_days"]
    config = {
        "Rules": [
            {
                "ID": "aws-cost-optimizer-default",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}],
                "Expiration": {"Days": expire_days},
            }
        ]
    }
    client.put_bucket_lifecycle_configuration(
        Bucket=resource,
        LifecycleConfiguration=config,
    )
    return True, f"Applied lifecycle policy (IA@30d, expire@{expire_days}d)"


def _apply_cloudfront(resource: str, settings: Dict) -> tuple[bool, str]:
    client = boto3.client("cloudfront")
    result = client.get_distribution_config(Id=resource)
    etag = result["ETag"]
    cfg = result["DistributionConfig"]

    behavior = cfg.get("DefaultCacheBehavior", {})
    ttl = settings["cloudfront_default_ttl"]
    behavior["DefaultTTL"] = ttl
    if behavior.get("MinTTL", 0) > ttl:
        behavior["MinTTL"] = ttl
    if behavior.get("MaxTTL", 0) < ttl:
        behavior["MaxTTL"] = ttl
    cfg["DefaultCacheBehavior"] = behavior

    client.update_distribution(
        Id=resource,
        IfMatch=etag,
        DistributionConfig=cfg,
    )
    return True, f"Updated default cache TTL to {ttl}s"


def _execute_recommendation(service: str, resource: str, settings: Dict) -> tuple[bool, str]:
    try:
        if service == "dynamodb":
            return _apply_dynamodb(resource, settings)
        if service == "lambda":
            return _apply_lambda(resource, settings)
        if service == "s3":
            return _apply_s3(resource, settings)
        if service == "cloudfront":
            return _apply_cloudfront(resource, settings)
        return False, f"Unsupported service: {service}"
    except ClientError as err:
        code = err.response.get("Error", {}).get("Code", "Unknown")
        return False, f"AWS error {code}: {err}"
    except Exception as err:
        return False, str(err)


def _apply_recommendation(rec: Dict, dry_run: bool, execute: bool, settings: Dict) -> bool:
    service = rec["service"].lower()
    resource = rec["resource"]

    if dry_run:
        console.print(f"[yellow]DRY RUN: Would optimize {service}/{resource}[/yellow]")
        return True

    if not execute:
        console.print(
            f"[yellow]Skipped {service}/{resource}[/yellow] "
            "[dim](set --execute or use menu option 5)[/dim]"
        )
        return False

    ok, msg = _execute_recommendation(service, resource, settings)
    if ok:
        console.print(f"[green]Applied {service}/{resource}[/green] — {msg}")
    else:
        console.print(f"[red]Failed {service}/{resource}[/red] — {msg}")
    return ok


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx: click.Context):
    """AWS Cost Optimizer - Find and fix cost inefficiencies"""
    if ctx.invoked_subcommand is None:
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
@click.option("--execute", is_flag=True, help="Execute AWS changes (default is non-mutating)")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt for bulk apply")
@click.option("--lambda-concurrency", default=10, show_default=True, type=int)
@click.option("--dynamodb-rcu", default=5, show_default=True, type=int)
@click.option("--dynamodb-wcu", default=5, show_default=True, type=int)
@click.option("--cloudfront-default-ttl", default=3600, show_default=True, type=int)
@click.option("--s3-expire-days", default=365, show_default=True, type=int)
def apply(
    service: str,
    resource: str | None,
    apply_all: bool,
    dry_run: bool,
    execute: bool,
    yes: bool,
    lambda_concurrency: int,
    dynamodb_rcu: int,
    dynamodb_wcu: int,
    cloudfront_default_ttl: int,
    s3_expire_days: int,
):
    """Apply cost optimization to one resource or all recommendations."""
    settings = {
        "lambda_concurrency": lambda_concurrency,
        "dynamodb_rcu": dynamodb_rcu,
        "dynamodb_wcu": dynamodb_wcu,
        "cloudfront_default_ttl": cloudfront_default_ttl,
        "s3_expire_days": s3_expire_days,
    }

    if apply_all:
        recs = _collect_recommendations(service)
        if not recs:
            console.print("[green]Nothing to apply.[/green]")
            return

        mode = "DRY RUN" if dry_run else ("EXECUTE" if execute else "PLAN")
        console.print(
            f"[bold cyan]Applying {len(recs)} recommendation(s) in scope: {service} ({mode})[/bold cyan]"
        )
        if execute and not dry_run and not yes:
            confirmed = Confirm.ask("Proceed with live apply-all?", default=False)
            if not confirmed:
                console.print("[yellow]Canceled.[/yellow]")
                return

        ok_count = 0
        for rec in recs:
            if _apply_recommendation(rec, dry_run=dry_run, execute=execute, settings=settings):
                ok_count += 1
        console.print(f"[green]Apply-all run complete.[/green] Success: {ok_count}/{len(recs)}")
        return

    if not resource:
        raise click.UsageError(
            "For single-resource apply, pass RESOURCE. "
            "Example: aws-cost-optimizer apply --service dynamodb my-table --dry-run\n"
            "Or use --all for bulk mode."
        )

    if service == "all":
        raise click.UsageError("Single-resource apply requires a specific --service (not 'all').")

    _apply_recommendation({"service": service, "resource": resource}, dry_run=dry_run, execute=execute, settings=settings)


@main.command()
def menu():
    """Launch interactive hub menu (WonderDash-style flow)."""
    if not sys.stdin.isatty():
        console.print("[red]Interactive menu requires a terminal (TTY).[/red]")
        return

    default_settings = {
        "lambda_concurrency": 10,
        "dynamodb_rcu": 5,
        "dynamodb_wcu": 5,
        "cloudfront_default_ttl": 3600,
        "s3_expire_days": 365,
    }

    while True:
        console.print(
            Panel(
                "[bold cyan]AWS Cost Optimizer Hub[/bold cyan]\n"
                "[1] Analyze all services\n"
                "[2] Analyze one service\n"
                "[3] Apply all (dry-run)\n"
                "[4] Apply one resource (dry-run)\n"
                "[5] Apply all (EXECUTE)\n"
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
                _apply_recommendation(rec, dry_run=True, execute=False, settings=default_settings)
        elif choice == 4:
            service = Prompt.ask("Service", choices=SERVICES[1:], default="dynamodb")
            resource = Prompt.ask("Resource")
            _apply_recommendation(
                {"service": service, "resource": resource},
                dry_run=True,
                execute=False,
                settings=default_settings,
            )
        elif choice == 5:
            service = Prompt.ask("Scope", choices=SERVICES, default="all")
            recs = _collect_recommendations(service)
            if not recs:
                console.print("[green]Nothing to apply.[/green]")
                continue
            _render_recommendations(recs)
            if not Confirm.ask("Run LIVE apply for these recommendations?", default=False):
                console.print("[yellow]Canceled.[/yellow]")
                continue
            ok_count = 0
            for rec in recs:
                if _apply_recommendation(rec, dry_run=False, execute=True, settings=default_settings):
                    ok_count += 1
            console.print(f"[green]Live apply finished.[/green] Success: {ok_count}/{len(recs)}")
        else:
            console.print("[red]Invalid choice.[/red]")


if __name__ == "__main__":
    main()
