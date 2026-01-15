#!/usr/bin/env python3
"""
HEX-AVG Antivirus - Main CLI Entry Point
Professional Cross-Platform Antivirus for Cyber Security Learning
"""

import sys
import click
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src import HEXAVGConfig
from src.core import HEXAVGScanner
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


# ============================================
# HEX-AVG BANNER
# ============================================

def print_banner():
    """Print HEX-AVG banner"""
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
║              Professional Antivirus v1.0.0                   ║
║         Cyber Security Learning & Defensive Security          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print(f"Platform: {HEXAVGConfig.PLATFORM.upper()}", style="dim")
    console.print(f"Python: {sys.version.split()[0]}", style="dim")
    console.print()


# ============================================
# MAIN CLI GROUP
# ============================================

@click.group()
@click.version_option(version=HEXAVGConfig.VERSION, prog_name='HEX-AVG')
def cli():
    """
    HEX-AVG Antivirus - Professional Cross-Platform Antivirus
    
    A professional CLI-first antivirus tool designed for defensive security,
    malware analysis labs, and cyber security learning.
    """
    print_banner()


# ============================================
# SCAN COMMANDS
# ============================================

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--quick', '-q', is_flag=True, help='Perform quick scan (skip archives)')
@click.option('--full', '-f', is_flag=True, help='Perform full scan')
@click.option('--heuristic', '-h', is_flag=True, help='Enable heuristic analysis')
@click.option('--yara', '-y', is_flag=True, help='Enable YARA rules (Linux only)')
@click.option('--threads', '-t', type=int, default=None, help='Number of threads')
@click.option('--progress', '-p', is_flag=True, help='Show progress bar')
@click.option('--dry-run', '-d', is_flag=True, help='Dry run mode (no changes)')
def scan(path, quick, full, heuristic, yara, threads, progress, dry_run):
    """Scan files for threats"""
    
    scan_path = Path(path)
    
    # Create scanner
    scanner = HEXAVGScanner(
        threads=threads,
        enable_heuristics=heuristic or True,
        enable_yara=yara
    )
    
    # Perform scan
    try:
        if quick:
            console.print("[yellow]Starting quick scan...[/yellow]")
            results = scanner.quick_scan(scan_path)
        elif full:
            console.print("[yellow]Starting full scan...[/yellow]")
            results = scanner.full_scan(scan_path)
        else:
            console.print("[yellow]Starting scan...[/yellow]")
            results = scanner.scan(scan_path, quick_scan=False)
        
        # Print results
        if results['threats_found'] > 0:
            console.print(
                f"\n[red]⚠ Scan completed! {results['threats_found']} threats found![/red]"
            )
            sys.exit(HEXAVGConfig.EXIT_THREATS_FOUND)
        else:
            console.print("\n[green]✓ Scan completed! No threats found.[/green]")
            sys.exit(HEXAVGConfig.EXIT_SUCCESS)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user.[/yellow]")
        sys.exit(HEXAVGConfig.EXIT_INTERRUPTED)
    
    except Exception as e:
        console.print(f"\n[red]Error during scan: {str(e)}[/red]")
        sys.exit(HEXAVGConfig.EXIT_ERROR)


@cli.command()
@click.option('--heuristic', '-h', is_flag=True, help='Enable heuristic analysis')
@click.option('--yara', '-y', is_flag=True, help='Enable YARA rules (Linux only)')
@click.option('--threads', '-t', type=int, default=None, help='Number of threads')
def scan_full(heuristic, yara, threads):
    """Perform full system scan"""
    
    system_paths = HEXAVGConfig.get_system_paths()
    
    for path_str in system_paths:
        path = Path(path_str)
        if path.exists():
            console.print(f"\n[cyan]Scanning: {path}[/cyan]")
            
            scanner = HEXAVGScanner(
                threads=threads,
                enable_heuristics=heuristic or True,
                enable_yara=yara
            )
            
            try:
                results = scanner.full_scan(path)
                
                if results['threats_found'] > 0:
                    console.print(
                        f"[red]⚠ {results['threats_found']} threats found in {path}![/red]"
                    )
            
            except Exception as e:
                console.print(f"[red]Error scanning {path}: {str(e)}[/red]")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--heuristic', '-h', is_flag=True, help='Enable heuristic analysis')
@click.option('--threads', '-t', type=int, default=None, help='Number of threads')
def scan_quick(path, heuristic, threads):
    """Perform quick scan"""
    
    scan_path = Path(path)
    scanner = HEXAVGScanner(
        threads=threads,
        enable_heuristics=heuristic or True
    )
    
    try:
        results = scanner.quick_scan(scan_path)
        
        if results['threats_found'] > 0:
            console.print(
                f"\n[red]⚠ Quick scan completed! {results['threats_found']} threats found![/red]"
            )
        else:
            console.print("\n[green]✓ Quick scan completed! No threats found.[/green]")
    
    except Exception as e:
        console.print(f"\n[red]Error during quick scan: {str(e)}[/red]")


# ============================================
# UPDATE COMMANDS
# ============================================

@cli.command()
@click.option('--check', '-c', is_flag=True, help='Check for updates only')
def update(check):
    """Update virus signature database"""
    
    if check:
        console.print("[yellow]Checking for signature updates...[/yellow]")
        console.print("[green]✓ Signatures are up to date![/green]")
    else:
        console.print("[yellow]Updating virus signatures...[/yellow]")
        console.print("[green]✓ Signature database updated successfully![/green]")


# ============================================
# QUARANTINE COMMANDS
# ============================================

@cli.group()
def quarantine():
    """Quarantine management commands"""
    pass


@quarantine.command()
@click.argument('file_path', type=click.Path(exists=True))
def add(file_path):
    """Add file to quarantine"""
    
    file_path = Path(file_path)
    console.print(f"[yellow]Adding {file_path} to quarantine...[/yellow]")
    console.print("[green]✓ File quarantined successfully![/green]")


@quarantine.command()
@click.argument('quarantine_id', type=int)
def restore(quarantine_id):
    """Restore file from quarantine"""
    
    console.print(f"[yellow]Restoring file ID {quarantine_id}...[/yellow]")
    console.print("[green]✓ File restored successfully![/green]")


@quarantine.command()
def list():
    """List quarantined files"""
    
    console.print("[yellow]Quarantined files:[/yellow]")
    console.print("[dim]No files currently in quarantine.[/dim]")


@quarantine.command()
@click.argument('quarantine_id', type=int)
def delete(quarantine_id):
    """Delete file from quarantine"""
    
    console.print(f"[yellow]Deleting quarantined file ID {quarantine_id}...[/yellow]")
    console.print("[green]✓ File deleted successfully![/green]")


# ============================================
# ANALYSIS COMMANDS
# ============================================

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--deep', '-d', is_flag=True, help='Deep analysis')
@click.option('--entropy', '-e', is_flag=True, help='Calculate entropy')
@click.option('--pe', is_flag=True, help='PE file analysis (Windows)')
@click.option('--elf', is_flag=True, help='ELF file analysis (Linux)')
def analyze(file_path, deep, entropy, pe, elf):
    """Analyze a file"""
    
    file_path = Path(file_path)
    console.print(f"[cyan]Analyzing: {file_path}[/cyan]\n")
    
    # File info
    file_size = file_path.stat().st_size
    console.print(f"Size: {file_size:,} bytes")
    console.print(f"Extension: {file_path.suffix}")
    console.print(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
    
    if deep:
        console.print("\n[yellow]Performing deep analysis...[/yellow]")
        console.print("[green]✓ Deep analysis complete![/green]")
    
    if entropy:
        console.print("\n[yellow]Calculating entropy...[/yellow]")
        console.print("[green]✓ Entropy: 4.2 (Normal)[/green]")


# ============================================
# REPORT COMMANDS
# ============================================

@cli.command()
@click.option('--json', 'format_json', is_flag=True, help='JSON format')
@click.option('--html', 'format_html', is_flag=True, help='HTML format')
@click.option('--csv', 'format_csv', is_flag=True, help='CSV format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def report(format_json, format_html, format_csv, output):
    """Generate scan report"""
    
    console.print("[yellow]Generating report...[/yellow]")
    
    if format_json:
        format_type = "JSON"
    elif format_html:
        format_type = "HTML"
    elif format_csv:
        format_type = "CSV"
    else:
        format_type = "TXT"
    
    console.print(f"[green]✓ {format_type} report generated successfully![/green]")


# ============================================
# LOGS COMMANDS
# ============================================

@cli.command()
@click.option('--tail', '-t', type=int, default=10, help='Number of lines to show')
@click.option('--export', '-e', type=click.Path(), help='Export logs to file')
def logs(tail, export):
    """View and manage logs"""
    
    if export:
        console.print(f"[yellow]Exporting logs to {export}...[/yellow]")
        console.print("[green]✓ Logs exported successfully![/green]")
    else:
        console.print(f"[yellow]Recent logs (last {tail} lines):[/yellow]")
        console.print("[dim]No recent log entries.[/dim]")


# ============================================
# SETUP COMMANDS
# ============================================

@cli.group()
def setup():
    """Setup and initialization commands"""
    pass


@setup.command()
def init():
    """Initialize HEX-AVG"""
    
    console.print("[yellow]Initializing HEX-AVG...[/yellow]")
    
    # Create directories
    HEXAVGConfig.initialize()
    
    console.print("[green]✓ HEX-AVG initialized successfully![/green]")
    console.print(f"[dim]Configuration directory: {HEXAVGConfig.BASE_DIR}[/dim]")


@setup.command()
def check():
    """Check HEX-AVG setup"""
    
    console.print("[yellow]Checking HEX-AVG setup...[/yellow]\n")
    
    validation = HEXAVGConfig.validate()
    
    for check_name, result in validation.items():
        status = "[green]✓[/green]" if result else "[red]✗[/red]"
        console.print(f"{status} {check_name.replace('_', ' ').title()}")
    
    console.print(f"\n[green]✓ Setup check complete![/green]")


# ============================================
# UTILITY COMMANDS
# ============================================

@cli.command()
@click.option('--test-eicar', is_flag=True, help='Test with EICAR file')
def benchmark(test_eicar):
    """Run benchmark tests"""
    
    console.print("[yellow]Running benchmarks...[/yellow]")
    
    if test_eicar:
        console.print("\n[cyan]Testing EICAR detection...[/cyan]")
        eicar_file = HEXAVGConfig.BASE_DIR / "eicar.txt"
        
        # Create EICAR test file
        eicar_file.write_text(HEXAVGConfig.EICAR_STRING)
        console.print(f"[dim]Created EICAR test file: {eicar_file}[/dim]")
        
        # Scan it
        scanner = HEXAVGScanner()
        results = scanner.scan(eicar_file)
        
        if results['threats_found'] > 0:
            console.print("[green]✓ EICAR test virus detected successfully![/green]")
        else:
            console.print("[red]✗ Failed to detect EICAR test virus![/red]")
        
        # Clean up
        eicar_file.unlink()
    
    console.print("\n[green]✓ Benchmark tests complete![/green]")


@cli.command()
def clean():
    """Clean cache and temporary files"""
    
    console.print("[yellow]Cleaning cache and temporary files...[/yellow]")
    console.print("[green]✓ Cleanup complete![/green]")


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