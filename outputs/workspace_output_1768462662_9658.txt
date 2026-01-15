"""
HEX-AVG v3.0.0 - Level-2+ Security Tool
Advanced antivirus with GUI, auto-update, ML scoring, and more
"""

import sys
import platform
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.scanner import Scanner
from src.detection.signature import SignatureDatabase
from src.detection.heuristic import HeuristicAnalyzer
from src.detection.advanced_heuristic import AdvancedHeuristicEngine
from src.detection.ml_scoring import get_ml_scorer
from src.update.update_manager import UpdateManager
from src.cloud.cloud_sync import get_cloud_client
from src.defender_integration import get_defender_integrator
from config import HEXAVGConfig

# Initialize Rich console
console = Console()


# CLI Groups
@click.group()
@click.version_option(version=HEXAVGConfig.VERSION)
def cli():
    """HEX-AVG v3.0.0 - Advanced Cross-Platform Antivirus for Cyber Security"""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--quick', is_flag=True, help='Quick scan of common locations')
@click.option('--full', is_flag=True, help='Full system scan')
@click.option('--threads', type=int, default=HEXAVGConfig.DEFAULT_THREADS, help='Number of threads')
@click.option('--output', type=click.Path(), help='Save report to file')
@click.option('--ml', is_flag=True, help='Enable ML-based scoring (experimental)')
@click.option('--cloud', is_flag=True, help='Enable cloud signature lookup')
def scan(path, quick, full, threads, output, ml, cloud):
    """
    Scan files or directories for threats
    
    Examples:
      hex-avg scan --quick
      hex-avg scan /path/to/scan
      hex-avg scan C:\\Users\\Downloads --ml --cloud
    """
    # Determine scan path
    if quick:
        scan_path = str(HEXAVGConfig.BASE_DIR / "test_data")  # For testing
        rprint("[yellow]⚡ Running quick scan...[/yellow]")
    elif full:
        scan_path = "/"
        rprint("[yellow]🔍 Running full system scan...[/yellow]")
    else:
        scan_path = path or "."
        rprint(f"[yellow]🔍 Scanning: {scan_path}[/yellow]")
    
    # Initialize components
    scanner = Scanner(threads=threads)
    signature_db = SignatureDatabase()
    heuristic_analyzer = HeuristicAnalyzer()
    advanced_heuristic = AdvancedHeuristicEngine()
    ml_scorer = get_ml_scorer() if ml else None
    cloud_client = get_cloud_client() if cloud else None
    
    # Run scan
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning...", total=None)
        
        for file_path, threat in scanner.scan_directory(scan_path):
            # Signature-based detection
            signature_result = signature_db.check_file(file_path)
            
            # Heuristic detection
            heuristic_result = heuristic_analyzer.analyze_file(file_path)
            advanced_heuristic_result = advanced_heuristic.analyze_file(Path(file_path))
            
            # ML scoring
            ml_result = None
            if ml_scorer:
                ml_result = ml_scorer.score_file(Path(file_path), advanced_heuristic_result)
            
            # Cloud lookup
            cloud_result = None
            if cloud_client:
                cloud_result = cloud_client.query_hash(Path(file_path))
            
            # Combine results
            if signature_result['threat_found'] or \
               advanced_heuristic_result['risk_score'] >= 50:
                results.append({
                    'file': file_path,
                    'signature': signature_result,
                    'heuristic': advanced_heuristic_result,
                    'ml': ml_result,
                    'cloud': cloud_result
                })
            
            progress.update(task, description=f"Scanning: {Path(file_path).name}")
    
    # Display results
    _display_scan_results(results, output)


@cli.command()
@click.option('--enable', is_flag=True, help='Start background protection')
@click.option('--disable', is_flag=True, help='Stop background protection')
@click.option('--status', is_flag=True, help='Show protection status')
def protection(enable, disable, status):
    """
    Start/stop background protection
    """
    if enable:
        rprint("[green]✅ Starting background protection...[/green]")
        rprint("[yellow]⚠️  Background protection feature requires LEVEL-2 implementation[/yellow]")
        rprint("[blue]ℹ️  Use: python hex_avg_level2.py start[/blue]")
    
    elif disable:
        rprint("[red]⏸ Stopping background protection...[/red]")
        rprint("[yellow]⚠️  Background protection feature requires LEVEL-2 implementation[/yellow]")
        rprint("[blue]ℹ️  Use: python hex_avg_level2.py stop[/blue]")
    
    elif status:
        rprint("[blue]📊 Protection Status:[/blue]")
        rprint("[yellow]⚠️  Background protection feature requires LEVEL-2 implementation[/yellow]")
        rprint("[blue]ℹ️  Use: python hex_avg_level2.py status[/blue]")
    
    else:
        rprint("[yellow]Usage: hex-avg protection --enable|--disable|--status[/yellow]")


@cli.command()
def update():
    """
    Check for and apply updates
    """
    rprint("[blue]🔄 Checking for updates...[/blue]")
    
    update_manager = UpdateManager()
    update_info = update_manager.check_for_updates()
    
    if update_info:
        rprint(Panel.fit(
            f"[green]Update Available![/green]\n\n"
            f"Current: {update_info['current_version']}\n"
            f"Latest: {update_info['latest_version']}\n\n"
            f"Release: {update_info['release_name']}\n"
            f"Date: {update_info['release_date']}",
            title="Update Available"
        ))
        
        if click.confirm("Do you want to update now?"):
            if update_manager.update_tool(update_info):
                rprint("[green]✅ Update successful![/green]")
                rprint("[blue]ℹ️  Please restart HEX-AVG[/blue]")
            else:
                rprint("[red]❌ Update failed[/red]")
    else:
        rprint("[green]✅ You're already on the latest version[/green]")


@cli.command()
def rules():
    """
    Update virus signatures and detection rules
    """
    rprint("[blue]📥 Updating virus signatures...[/blue]")
    
    update_manager = UpdateManager()
    if update_manager.update_rules():
        rprint("[green]✅ Signatures updated successfully[/green]")
    else:
        rprint("[yellow]⚠️  Signature update not available[/yellow]")


@cli.group()
def cloud():
    """Cloud signature sync management"""
    pass


@cloud.command()
@click.option('--show-notice', is_flag=True, help='Show privacy notice')
def enable(show_notice):
    """Enable cloud signature sync"""
    cloud_client = get_cloud_client()
    cloud_client.enable(show_notice=show_notice)


@cloud.command()
def disable():
    """Disable cloud signature sync"""
    cloud_client = get_cloud_client()
    cloud_client.disable()


@cloud.command()
def status():
    """Show cloud sync status"""
    cloud_client = get_cloud_client()
    
    if cloud_client.is_enabled():
        stats = cloud_client.get_cache_stats()
        
        table = Table(title="Cloud Sync Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Status", "[green]Enabled[/green]")
        table.add_row("Cached Hashes", str(stats['total_cached_hashes']))
        table.add_row("Malicious", str(stats['malicious_hashes']))
        table.add_row("Benign", str(stats['benign_hashes']))
        table.add_row("Unknown", str(stats['unknown_hashes']))
        
        console.print(table)
    else:
        rprint("[red]❌ Cloud sync is disabled[/red]")
        rprint("[blue]ℹ️  Enable with: hex-avg cloud enable[/blue]")


@cloud.command()
def clear():
    """Clear cloud cache"""
    cloud_client = get_cloud_client()
    cloud_client.clear_cache()


@cli.group()
def quarantine():
    """Quarantine management"""
    pass


@quarantine.command()
def list():
    """List quarantined files"""
    rprint("[blue]📋 Quarantined Files:[/blue]")
    rprint("[yellow]⚠️  Quarantine feature requires LEVEL-2 implementation[/yellow]")
    rprint("[blue]ℹ️  Use: python hex_avg_level2.py quarantine list[/blue]")


@quarantine.command()
def clear():
    """Clear quarantine"""
    if click.confirm("Are you sure you want to clear all quarantined files?"):
        rprint("[yellow]⚠️  Quarantine feature requires LEVEL-2 implementation[/yellow]")


@cli.command()
def gui():
    """
    Launch HEX-AVG GUI
    """
    try:
        from src.gui.main_window import launch_gui
        rprint("[blue]🖥️  Launching HEX-AVG GUI...[/blue]")
        launch_gui()
    except Exception as e:
        rprint(f"[red]❌ Failed to launch GUI: {str(e)}[/red]")
        rprint("[yellow]Make sure Tkinter is installed: pip install tk[/yellow]")


@cli.command()
def defender():
    """
    Show Windows Defender integration status
    """
    defender_integrator = get_defender_integrator()
    defender_integrator.show_coexistence_notice()
    
    status = defender_integrator.get_coexistence_info()
    
    console.print(Panel.fit(
        f"Defender Status: [green]{status['defender_status']}[/green]\n"
        f"Coexistence Mode: [cyan]{status['coexistence_mode']}[/cyan]\n"
        f"Philosophy: [magenta]{status['philosophy']}[/magenta]\n\n"
        f"Benefits:\n" + "\n".join(f"  • {b}" for b in status['benefits'][:3]),
        title="Windows Defender Integration"
    ))


@cli.command()
def version():
    """Show version information"""
    table = Table(title="HEX-AVG Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Status", style="green")
    
    table.add_row("HEX-AVG", HEXAVGConfig.VERSION, "Active")
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "Active")
    table.add_row("Advanced Heuristics", "1.0.0", "Active")
    table.add_row("ML Scoring", "1.0.0-exp", "Experimental")
    table.add_row("Cloud Sync", "1.0.0", "Optional")
    
    console.print(table)


def _display_scan_results(results, output_file=None):
    """Display scan results"""
    if not results:
        rprint("[green]✅ No threats found![/green]")
        return
    
    # Display results
    table = Table(title="Scan Results")
    table.add_column("File", style="cyan")
    table.add_column("Signature", style="red")
    table.add_column("Heuristic", style="yellow")
    table.add_column("ML Score", style="magenta")
    
    for result in results:
        sig = "✓" if result['signature']['threat_found'] else "✗"
        heur_score = result['heuristic']['risk_score']
        ml_score = result['ml']['ml_score'] if result['ml'] else "N/A"
        
        table.add_row(
            Path(result['file']).name,
            sig,
            f"{heur_score}/100",
            f"{ml_score}" if ml_score != "N/A" else "N/A"
        )
    
    console.print(table)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            for result in results:
                f.write(f"File: {result['file']}\n")
                f.write(f"  Signature: {result['signature']}\n")
                f.write(f"  Heuristic: {result['heuristic']}\n")
                if result['ml']:
                    f.write(f"  ML: {result['ml']}\n")
                f.write("\n")
        
        rprint(f"[green]✅ Report saved to {output_file}[/green]")


if __name__ == "__main__":
    # Show Windows Defender notice on Windows
    if platform.system().lower() == 'windows':
        defender_integrator = get_defender_integrator()
        defender_integrator.show_coexistence_notice()
    
    cli()