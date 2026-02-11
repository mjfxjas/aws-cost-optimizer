"""CLI for AWS Cost Optimizer"""
import click
from rich.console import Console
from rich.table import Table
from . import analyzers

console = Console()

@click.group()
@click.version_option()
def main():
    """AWS Cost Optimizer - Find and fix cost inefficiencies"""
    pass

@main.command()
@click.option('--service', type=click.Choice(['all', 'dynamodb', 'lambda', 's3', 'cloudfront']), default='all')
def analyze(service):
    """Analyze AWS resources for cost optimization opportunities"""
    console.print(f"[bold cyan]Analyzing {service} for cost optimization...[/bold cyan]\n")
    
    recommendations = []
    
    if service in ['all', 'dynamodb']:
        recommendations.extend(analyzers.analyze_dynamodb())
    if service in ['all', 'lambda']:
        recommendations.extend(analyzers.analyze_lambda())
    if service in ['all', 's3']:
        recommendations.extend(analyzers.analyze_s3())
    if service in ['all', 'cloudfront']:
        recommendations.extend(analyzers.analyze_cloudfront())
    
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
            rec['service'],
            rec['resource'],
            rec['issue'],
            rec['savings'],
            rec['action']
        )
    
    console.print(table)
    console.print(f"\n[bold]Total recommendations: {len(recommendations)}[/bold]")

@main.command()
@click.argument('service')
@click.argument('resource')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
def apply(service, resource, dry_run):
    """Apply cost optimization to a specific resource"""
    if dry_run:
        console.print(f"[yellow]DRY RUN: Would optimize {service}/{resource}[/yellow]")
    else:
        console.print(f"[green]Optimizing {service}/{resource}...[/green]")
        # Implementation would go here
        console.print("[green]Optimization applied![/green]")

@main.command()
def report():
    """Generate cost optimization report"""
    console.print("[bold cyan]Cost Optimization Report[/bold cyan]\n")
    console.print("Feature coming soon!")

if __name__ == '__main__':
    main()
