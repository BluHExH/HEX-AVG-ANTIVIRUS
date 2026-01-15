"""
HEX-AVG CLI - Consolidated Command Line Interface
==================================================

This module contains all CLI commands for HEX-AVG v3.0.0
Features:
- Manual virus scanning
- Background protection management
- Auto-update system
- Cloud signature sync (optional)
- GUI launcher
- Windows Defender integration
- ML-based scoring (experimental)
- Advanced heuristic detection
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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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


# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version=HEXAVGConfig.VERSION, prog_name="HEX-AVG")
def cli():
    """
    HEX-AVG v3.0.0 - Advanced Cross-Platform Antivirus for Cyber Security
    
    A professional-grade antivirus tool designed for cybersecurity education,
    malware analysis labs, and defensive security operations.
    """
    pass


# ============================================================================
# SCAN COMMANDS
# ============================================================================

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--quick', is_flag=True, help='Quick scan of common locations')
@click.option('--full', is_flag=True, help='Full system scan')
@click.option('--threads', type=int, default=HEXAVGConfig.DEFAULT_THREADS, 
              help='Number of threads for parallel scanning')
@click.option('--output', type=click.Path(), help='Save scan report to file')
@click.option('--ml', is_flag=True, help='Enable ML-based scoring (experimental)')
@click.option('--cloud', is_flag=True, help='Enable cloud signature lookup')
@click.option('--deep', is_flag=True, help='Deep scan with all detection methods')
def scan(path, quick, full, threads, output, ml, cloud, deep):
    """
    Scan files or directories for threats
    
    Examples:
      hex-avg scan --quick
      hex-avg scan /path/to/scan
      hex-avg scan C:\\Users\\Downloads --ml --cloud
      hex-avg scan /home/user/documents --deep --output report.txt
    """
    # Determine scan path
    if quick:
        scan_path = str(HEXAVGConfig.BASE_DIR / "test_data")  # For testing
        rprint("[yellow]⚡ Running quick scan...[/yellow]")
    elif full:
        scan_path = "/" if platform.system().lower() != 'windows' else "C:\&quot;
        rprint("[yellow]🔍 Running full system scan...[/yellow]")
    else:
        scan_path = path or "."
        rprint(f"[yellow]🔍 Scanning: {scan_path}[/yellow]")
    
    # Initialize components
    rprint("[cyan]🔧 Initializing detection engines...[/cyan]")
    scanner = Scanner(threads=threads)
    signature_db = SignatureDatabase()
    heuristic_analyzer = HeuristicAnalyzer()
    advanced_heuristic = AdvancedHeuristicEngine()
    ml_scorer = get_ml_scorer() if ml else None
    cloud_client = get_cloud_client() if cloud else None
    
    # Run scan
    results = []
    files_scanned = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning...", total=None)
        
        for file_path, threat in scanner.scan_directory(scan_path):
            files_scanned += 1
            
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
            if cloud_client and cloud_client.is_enabled():
                cloud_result = cloud_client.query_hash(Path(file_path))
            
            # Combine results
            is_threat = (
                signature_result['threat_found'] or
                advanced_heuristic_result['risk_score'] >= 50 or
                (ml_result and ml_result['ml_score'] >= 0.7) or
                (cloud_result and cloud_result['is_malicious'])
            )
            
            if is_threat:
                results.append({
                    'file': file_path,
                    'signature': signature_result,
                    'heuristic': advanced_heuristic_result,
                    'ml': ml_result,
                    'cloud': cloud_result
                })
            
            progress.update(task, description=f"Scanning: {Path(file_path).name}")
    
    # Display results
    _display_scan_results(results, files_scanned, output)


def _display_scan_results(results, files_scanned, output_file=None):
    """Display scan results"""
    rprint(f"\n[blue]📊 Scan completed: {files_scanned} files scanned[/blue]")
    
    if not results:
        rprint("[green]✅ No threats found![/green]")
        return
    
    # Display results
    table = Table(title="Scan Results")
    table.add_column("File", style="cyan")
    table.add_column("Signature", style="red")
    table.add_column("Heuristic", style="yellow")
    table.add_column("ML Score", style="magenta")
    table.add_column("Cloud", style="blue")
    
    for result in results:
        sig = "✓" if result['signature']['threat_found'] else "✗"
        heur_score = result['heuristic']['risk_score']
        ml_score = result['ml']['ml_score'] if result['ml'] else "N/A"
        cloud = "✓" if result['cloud'] and result['cloud']['is_malicious'] else "✗"
        
        table.add_row(
            Path(result['file']).name,
            sig,
            f"{heur_score}/100",
            f"{ml_score:.2f}" if ml_score != "N/A" else "N/A",
            cloud
        )
    
    console.print(table)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(f"HEX-AVG Scan Report\n")
            f.write(f"Files Scanned: {files_scanned}\n")
            f.write(f"Threats Found: {len(results)}\n\n")
            
            for result in results:
                f.write(f"File: {result['file']}\n")
                f.write(f"  Signature: {result['signature']}\n")
                f.write(f"  Heuristic: {result['heuristic']}\n")
                if result['ml']:
                    f.write(f"  ML: {result['ml']}\n")
                if result['cloud']:
                    f.write(f"  Cloud: {result['cloud']}\n")
                f.write("\n")
        
        rprint(f"[green]✅ Report saved to {output_file}[/green]")


# ============================================================================
# PROTECTION COMMANDS
# ============================================================================

@cli.group()
def protection():
    """Background protection management"""
    pass


@protection.command()
@click.option('--enable', is_flag=True, help='Start background protection')
@click.option('--disable', is_flag=True, help='Stop background protection')
@click.option('--status', is_flag=True, help='Show protection status')
def manage(enable, disable, status):
    """Start/stop background protection"""
    if enable:
        rprint("[green]✅ Starting background protection...[/green]")
        rprint("[yellow]⚠️  Background protection requires LEVEL-2 implementation[/yellow]")
        rprint("[blue]ℹ️  This feature monitors file system changes in real-time[/blue]")
    
    elif disable:
        rprint("[red]⏸ Stopping background protection...[/red]")
        rprint("[yellow]⚠️  Background protection will stop monitoring[/yellow]")
    
    elif status:
        rprint("[blue]📊 Protection Status:[/blue]")
        rprint("[yellow]⚠️  Background protection not currently implemented[/yellow]")
        rprint("[blue]ℹ️  Use: hex-avg protection --enable to start monitoring[/blue]")
    
    else:
        rprint("[yellow]Usage: hex-avg protection manage --enable|--disable|--status[/yellow]")


@protection.command()
def status():
    """Show current protection status"""
    rprint("[blue]📊 Protection Status:[/blue]")
    rprint("[red]⚠️  Background protection is not active[/red]")
    rprint("[cyan]Real-time monitoring: DISABLED[/cyan]")
    rprint("[cyan]Scheduled scans: NOT CONFIGURED[/cyan]")
    rprint("\n[blue]ℹ️  Use 'hex-avg protection manage --enable' to start protection[/blue]")


# ============================================================================
# UPDATE COMMANDS
# ============================================================================

@cli.command()
def update():
    """
    Check for and apply HEX-AVG updates
    
    This command checks GitHub Releases for the latest version
    and prompts you to update if a newer version is available.
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
    
    This command downloads the latest virus signatures and YARA rules
    from the HEX-AVG repository.
    """
    rprint("[blue]📥 Updating virus signatures...[/blue]")
    
    update_manager = UpdateManager()
    if update_manager.update_rules():
        rprint("[green]✅ Signatures updated successfully[/green]")
        rprint("[cyan]Signature database updated[/cyan]")
    else:
        rprint("[yellow]⚠️  Signature update not available[/yellow]")


# ============================================================================
# CLOUD SYNC COMMANDS
# ============================================================================

@cli.group()
def cloud():
    """Cloud signature sync management (optional)"""
    pass


@cloud.command()
@click.option('--show-notice', is_flag=True, help='Show privacy notice before enabling')
def enable(show_notice):
    """
    Enable cloud signature sync
    
    This feature allows HEX-AVG to query a cloud database for known
    malicious file hashes. Only file hashes are sent, no file content.
    """
    cloud_client = get_cloud_client()
    cloud_client.enable(show_notice=show_notice)


@cloud.command()
def disable():
    """Disable cloud signature sync"""
    cloud_client = get_cloud_client()
    cloud_client.disable()
    rprint("[yellow]⚠️  Cloud sync disabled[/yellow]")


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
    rprint("[green]✅ Cloud cache cleared[/green]")


# ============================================================================
# QUARANTINE COMMANDS
# ============================================================================

@cli.group()
def quarantine():
    """Quarantine management"""
    pass


@quarantine.command()
def list_files():
    """List quarantined files"""
    rprint("[blue]📋 Quarantined Files:[/blue]")
    rprint("[yellow]⚠️  Quarantine feature requires LEVEL-2 implementation[/yellow]")
    rprint("[cyan]No files are currently quarantined[/cyan]")


@quarantine.command()
def clear_all():
    """Clear all quarantined files"""
    if click.confirm("Are you sure you want to clear all quarantined files?"):
        rprint("[yellow]⚠️  Quarantine feature requires LEVEL-2 implementation[/yellow]")


# ============================================================================
# GUI COMMAND
# ============================================================================

@cli.command()
def gui():
    """
    Launch HEX-AVG Graphical User Interface
    
    This launches the Tkinter-based GUI for a more user-friendly experience.
    """
    try:
        from src.gui.main_window import launch_gui
        rprint("[blue]🖥️  Launching HEX-AVG GUI...[/blue]")
        launch_gui()
    except Exception as e:
        rprint(f"[red]❌ Failed to launch GUI: {str(e)}[/red]")
        rprint("[yellow]Make sure Tkinter is installed: pip install tk[/yellow]")


# ============================================================================
# DEFENDER INTEGRATION
# ============================================================================

@cli.command()
def defender():
    """
    Show Windows Defender integration status
    
    HEX-AVG is designed to coexist with Windows Defender and other
    antivirus software. It never disables or modifies Defender.
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


# ============================================================================
# VERSION INFO
# ============================================================================

@cli.command()
def version():
    """
    Show detailed version information
    
    Displays version information for HEX-AVG and all its components.
    """
    table = Table(title="HEX-AVG Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Status", style="green")
    
    table.add_row("HEX-AVG", HEXAVGConfig.VERSION, "Active")
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "Active")
    table.add_row("Advanced Heuristics", "1.0.0", "Active")
    table.add_row("ML Scoring", "1.0.0-exp", "Experimental")
    table.add_row("Cloud Sync", "1.0.0", "Optional")
    table.add_row("YARA Rules", "1.0.0", "Active" if platform.system().lower() == 'linux' else "N/A")
    
    console.print(table)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for HEX-AVG CLI"""
    
    # Show Windows Defender notice on Windows
    if platform.system().lower() == 'windows':
        defender_integrator = get_defender_integrator()
        defender_integrator.show_coexistence_notice()
    
    # Run CLI
    cli()


if __name__ == "__main__":
    main()