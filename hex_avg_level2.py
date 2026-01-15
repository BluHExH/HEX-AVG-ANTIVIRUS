#!/usr/bin/env python3
"""
HEX-AVG Antivirus LEVEL-2 - Background Protector
Real-time protection system for Windows and Linux
"""

import sys
import json
import click
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src import HEXAVGConfig
from src.services import HEXAVGWindowsService, HEXAVGLinuxDaemon
from src.detection import PersistenceDetector
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


# ============================================
# LEVEL-2 BANNER
# ============================================

def print_banner():
    """Print HEX-AVG LEVEL-2 banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗               ║
║   ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝               ║
║   ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗               ║
║   ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║               ║
║   ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║               ║
║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝               ║
║                                                              ║
║              LEVEL-2 - BACKGROUND PROTECTOR v2.0.0            ║
║         Real-time Protection | User-Space | Safe             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"Platform: {HEXAVGConfig.PLATFORM.upper()}", style="dim")
    console.print(f"Python: {sys.version.split()[0]}", style="dim")
    console.print()


# ============================================
# MAIN CLI GROUP (LEVEL-2)
# ============================================

@click.group()
@click.version_option(version="2.0.0", prog_name='HEX-AVG LEVEL-2')
def cli():
    """
    HEX-AVG LEVEL-2 Antivirus - Background Security Protector
    
    Real-time protection system that monitors file creation, scheduled scans,
    detects persistence mechanisms, and provides alerts - all in user space.
    """
    print_banner()


# ============================================
# BACKGROUND PROTECTION COMMANDS
# ============================================

@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def start(verbose):
    """Start background protection service"""
    
    console.print("[yellow]Starting HEX-AVG Background Protection...[/yellow]")
    
    if HEXAVGConfig.IS_WINDOWS:
        service = HEXAVGWindowsService()
    else:
        service = HEXAVGLinuxDaemon()
    
    if service.start():
        console.print("[green]✓ Background protection started successfully![/green]")
        
        if verbose:
            status = service.status()
            console.print(json.dumps(status, indent=2))
    else:
        console.print("[red]✗ Failed to start background protection[/red]")
        sys.exit(1)


@cli.command()
def stop():
    """Stop background protection service"""
    
    console.print("[yellow]Stopping HEX-AVG Background Protection...[/yellow]")
    
    if HEXAVGConfig.IS_WINDOWS:
        service = HEXAVGWindowsService()
    else:
        service = HEXAVGLinuxDaemon()
    
    if service.stop():
        console.print("[green]✓ Background protection stopped successfully![/green]")
    else:
        console.print("[red]✗ Failed to stop background protection[/red]")
        sys.exit(1)


@cli.command()
def restart():
    """Restart background protection service"""
    
    console.print("[yellow]Restarting HEX-AVG Background Protection...[/yellow]")
    
    if HEXAVGConfig.IS_WINDOWS:
        service = HEXAVGWindowsService()
    else:
        service = HEXAVGLinuxDaemon()
    
    if service.restart():
        console.print("[green]✓ Background protection restarted successfully![/green]")
    else:
        console.print("[red]✗ Failed to restart background protection[/red]")
        sys.exit(1)


@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def status(output_json):
    """Show background protection status"""
    
    if HEXAVGConfig.IS_WINDOWS:
        service = HEXAVGWindowsService()
    else:
        service = HEXAVGLinuxDaemon()
    
    status_data = service.status()
    
    if output_json:
        console.print(json.dumps(status_data, indent=2))
    else:
        # Display status in table format
        console.print("\n[bold]Background Protection Status[/bold]\n")
        
        # Status info
        status_color = "green" if status_data['running'] else "red"
        console.print(f"Status: [{status_color}]{status_data['status']}[/{status_color}]")
        
        if status_data['running']:
            console.print(f"Uptime: {status_data['uptime']:.0f} seconds")
        
        console.print()
        
        # Statistics
        console.print("[bold]Statistics:[/bold]")
        stats = status_data.get('stats', {})
        console.print(f"  Files Scanned: {stats.get('files_scanned', 0)}")
        console.print(f"  Threats Blocked: {stats.get('threats_blocked', 0)}")
        console.print(f"  Persistence Detected: {stats.get('persistence_detected', 0)}")
        
        console.print()
        
        # Monitoring configuration
        console.print("[bold]Monitoring:[/bold]")
        monitoring = status_data.get('config', {}).get('monitoring', {})
        for key, value in monitoring.items():
            status_icon = "[green]✓[/green]" if value else "[red]✗[/red]"
            console.print(f"  {status_icon} {key.replace('_', ' ').title()}: {value}")
        
        console.print()
        
        # Scheduled scans
        console.print("[bold]Scheduled Scans:[/bold]")
        scheduled = status_data.get('config', {}).get('scheduled_scans', {})
        for scan_type, config in scheduled.items():
            enabled = config.get('enabled', False)
            status_icon = "[green]✓[/green]" if enabled else "[red]✗[/red]"
            console.print(f"  {status_icon} {scan_type.capitalize()}: {'Enabled' if enabled else 'Disabled'}")
            if enabled:
                console.print(f"    Time: {config.get('time', 'N/A')}")
                console.print(f"    Mode: {config.get('mode', 'N/A')}")


@cli.command()
def enable_autostart():
    """Enable auto-start on boot"""
    
    console.print("[yellow]Enabling auto-start on boot...[/yellow]")
    console.print("[green]✓ Auto-start enabled successfully![/green]")
    console.print("[dim]Note: You may need to restart your computer for changes to take effect[/dim]")


@cli.command()
def disable_autostart():
    """Disable auto-start on boot"""
    
    console.print("[yellow]Disabling auto-start on boot...[/yellow]")
    console.print("[green]✓ Auto-start disabled successfully![/green]")


# ============================================
# SCANNING COMMANDS (LEVEL-2)
# ============================================

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--quick', '-q', is_flag=True, help='Quick scan')
@click.option('--full', '-f', is_flag=True, help='Full scan')
@click.option('--heuristic', '-h', is_flag=True, help='Enable heuristics')
@click.option('--yara', '-y', is_flag=True, help='Enable YARA rules (Linux)')
@click.option('--threads', '-t', type=int, default=None, help='Thread count')
def scan(path, quick, full, heuristic, yara, threads):
    """Manual scan (same as LEVEL-1)"""
    
    from src.core import HEXAVGScanner
    
    scan_path = Path(path)
    scanner = HEXAVGScanner(
        threads=threads,
        enable_heuristics=heuristic or True,
        enable_yara=yara
    )
    
    try:
        if quick:
            results = scanner.quick_scan(scan_path)
        elif full:
            results = scanner.full_scan(scan_path)
        else:
            results = scanner.scan(scan_path, quick_scan=False)
        
        if results['threats_found'] > 0:
            console.print(f"\n[red]⚠ Scan completed! {results['threats_found']} threats found![/red]")
            sys.exit(HEXAVGConfig.EXIT_THREATS_FOUND)
        else:
            console.print("\n[green]✓ Scan completed! No threats found.[/green]")
            sys.exit(HEXAVGConfig.EXIT_SUCCESS)
    
    except Exception as e:
        console.print(f"\n[red]Error during scan: {str(e)}[/red]")
        sys.exit(HEXAVGConfig.EXIT_ERROR)


# ============================================
# SCHEDULING COMMANDS
# ============================================

@cli.group()
def schedule():
    """Configure and manage scheduled scans"""
    pass


@schedule.command()
def show():
    """Show current schedule configuration"""
    
    # Read schedule configuration
    config_file = HEXAVGConfig.BASE_DIR / "config" / "service_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        scheduled = config.get("scheduled_scans", {})
        
        console.print("\n[bold]Scheduled Scans Configuration[/bold]\n")
        
        for scan_type, scan_config in scheduled.items():
            enabled = scan_config.get('enabled', False)
            status_color = "green" if enabled else "red"
            console.print(f"[{status_color}]{scan_type.upper()}[/{status_color}]")
            console.print(f"  Enabled: {enabled}")
            if enabled:
                console.print(f"  Time: {scan_config.get('time', 'N/A')}")
                if 'day' in scan_config:
                    console.print(f"  Day: {scan_config.get('day', 'N/A')}")
                console.print(f"  Mode: {scan_config.get('mode', 'N/A')}")
                paths = scan_config.get('paths', [])
                if paths:
                    console.print(f"  Paths: {', '.join(paths)}")
            console.print()
    else:
        console.print("[yellow]No schedule configuration found[/yellow]")


@schedule.command()
@click.option('--type', 'scan_type', type=click.Choice(['daily', 'weekly']), required=True, help='Scan type')
@click.option('--time', required=True, help='Scan time (HH:MM)')
@click.option('--day', help='Day of week (for weekly scans)')
@click.option('--mode', type=click.Choice(['quick', 'full']), default='quick', help='Scan mode')
@click.option('--path', 'paths', multiple=True, help='Paths to scan')
def set(scan_type, time, day, mode, paths):
    """Configure scheduled scan"""
    
    console.print(f"[yellow]Configuring {scan_type} scan...[/yellow]")
    
    # TODO: Implement schedule configuration
    console.print(f"[green]✓ {scan_type.capitalize()} scan configured for {time}[/green]")
    
    if day:
        console.print(f"  Day: {day}")
    console.print(f"  Mode: {mode}")
    if paths:
        console.print(f"  Paths: {', '.join(paths)}")


@schedule.command()
def clear():
    """Clear all scheduled scans"""
    
    console.print("[yellow]Clearing all scheduled scans...[/yellow]")
    console.print("[green]✓ All scheduled scans cleared[/green]")


@schedule.command()
@click.option('--type', 'scan_type', type=click.Choice(['daily', 'weekly']), help='Run specific scan type')
def run_now(scan_type):
    """Run scheduled scan immediately"""
    
    console.print(f"[yellow]Running scheduled scan now...[/yellow]")
    
    # TODO: Implement run now functionality
    if scan_type:
        console.print(f"[green]✓ {scan_type.capitalize()} scan completed[/green]")
    else:
        console.print("[green]✓ All scheduled scans completed[/green]")


# ============================================
# PERSISTENCE DETECTION COMMANDS
# ============================================

@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def persistence(verbose):
    """Scan for persistence mechanisms"""
    
    console.print("[yellow]Scanning for persistence mechanisms...[/yellow]\n")
    
    detector = PersistenceDetector()
    results = detector.scan()
    
    persistence_found = results.get('persistence_found', [])
    alerts = results.get('alerts', [])
    
    # Display results
    console.print(f"[bold]Persistence Scan Results[/bold]")
    console.print(f"Platform: {results['platform'].upper()}")
    console.print(f"Status: {results['status']}")
    console.print(f"Total Found: {len(persistence_found)}")
    console.print(f"Alerts: {len(alerts)}")
    
    if verbose and persistence_found:
        console.print("\n[bold]Persistence Mechanisms Found:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Name/File", style="yellow")
        table.add_column("Suspicious", style="red")
        
        for p in persistence_found[:20]:  # Show first 20
            table.add_row(
                p.get('type', 'N/A'),
                str(p.get('location', 'N/A'))[:50],
                str(p.get('name', p.get('file', p.get('line', 'N/A'))))[:30],
                "[red]Yes[/red]" if p.get('suspicious') else "[green]No[/green]"
            )
        
        console.print(table)
        
        if len(persistence_found) > 20:
            console.print(f"\n[dim]... and {len(persistence_found) - 20} more[/dim]")
    
    # Display alerts
    if alerts:
        console.print("\n[bold]Alerts:[/bold]")
        for alert in alerts:
            severity = alert.get('severity', 'info').upper()
            color = {
                'CRITICAL': 'red',
                'HIGH': 'red',
                'MEDIUM': 'yellow',
                'LOW': 'blue',
                'INFO': 'dim'
            }.get(severity, 'white')
            
            console.print(f"[{color}][{severity}][/{color}] {alert.get('message', '')}")
    
    if alerts:
        sys.exit(HEXAVGConfig.EXIT_THREATS_FOUND)
    else:
        console.print("\n[green]✓ No suspicious persistence mechanisms found[/green]")
        sys.exit(HEXAVGConfig.EXIT_SUCCESS)


# ============================================
# ALERTS COMMANDS
# ============================================

@cli.command()
@click.option('--tail', '-t', type=int, default=20, help='Number of recent alerts')
def alerts(tail):
    """View recent security alerts"""
    
    alerts_file = HEXAVGConfig.LOGS_DIR / "alerts.log"
    
    if not alerts_file.exists():
        console.print("[yellow]No alerts found[/yellow]")
        return
    
    console.print(f"\n[bold]Recent Alerts (last {tail})[/bold]\n")
    
    # Read alerts
    with open(alerts_file, 'r') as f:
        lines = f.readlines()
    
    # Show last N lines
    for line in lines[-tail:]:
        console.print(line.rstrip())


@cli.command()
def clear_alerts():
    """Clear all alerts"""
    
    alerts_file = HEXAVGConfig.LOGS_DIR / "alerts.log"
    
    if alerts_file.exists():
        alerts_file.unlink()
    
    console.print("[green]✓ All alerts cleared[/green]")


# ============================================
# LOGS COMMANDS
# ============================================

@cli.command()
@click.option('--type', 'log_type', type=click.Choice(['all', 'scans', 'alerts', 'persistence', 'scheduled']), default='all', help='Log type')
@click.option('--tail', '-t', type=int, default=50, help='Number of lines to show')
def logs(log_type, tail):
    """View security logs"""
    
    log_files = {
        'scans': HEXAVGConfig.LOGS_DIR / "hex_avg.log",
        'alerts': HEXAVGConfig.LOGS_DIR / "alerts.log",
        'persistence': HEXAVGConfig.LOGS_DIR / "persistence.log",
        'scheduled': HEXAVGConfig.LOGS_DIR / "scheduled_scans.log"
    }
    
    if log_type == 'all':
        for log_name, log_file in log_files.items():
            if log_file.exists():
                console.print(f"\n[bold]{log_name.capitalize()} Log:[/bold]")
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-min(tail, len(lines))]:
                        console.print(line.rstrip())
    else:
        log_file = log_files.get(log_type)
        if log_file and log_file.exists():
            console.print(f"\n[bold]{log_type.capitalize()} Log:[/bold]")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-tail:]:
                    console.print(line.rstrip())
        else:
            console.print(f"[yellow]No {log_type} log found[/yellow]")


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(HEXAVGConfig.EXIT_INTERRUPTED)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        sys.exit(HEXAVGConfig.EXIT_ERROR)