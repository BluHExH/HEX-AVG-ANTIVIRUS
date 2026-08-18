"""
HEX-AVG CLI - Command Line Interface
=====================================

Educational / experimental defensive antivirus CLI.
"""

import sys
import platform
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Ensure repo root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import HEXAVGConfig
from src.core.scanner import HEXAVGScanner
from src.detection.signature import SignatureDetector
from src.detection.heuristic import HeuristicDetector

try:
    from src.detection.advanced_heuristic import AdvancedHeuristicEngine
except ImportError:
    AdvancedHeuristicEngine = None

try:
    from src.detection.ml_scoring import get_ml_scorer
except ImportError:
    def get_ml_scorer():
        raise RuntimeError("ML scoring module not available")

try:
    from src.update.update_manager import UpdateManager
except ImportError:
    UpdateManager = None

try:
    from src.cloud.cloud_sync import get_cloud_client
except ImportError:
    def get_cloud_client():
        raise RuntimeError("Cloud module not available")

try:
    from src.defender_integration import get_defender_integrator
except ImportError:
    def get_defender_integrator():
        raise RuntimeError("Defender integration not available")

console = Console()


@click.group()
@click.version_option(version=HEXAVGConfig.VERSION, prog_name="HEX-AVG")
def cli():
    """
    HEX-AVG - Educational Cross-Platform Antivirus

    Experimental defensive tool for cybersecurity learning and labs.
    Not a replacement for commercial antivirus software.
    """
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=False), required=False)
@click.option("--quick", is_flag=True, help="Quick scan mode")
@click.option("--full", is_flag=True, help="Full system scan (use with caution)")
@click.option("--threads", type=int, default=None, help="Number of scan threads")
@click.option("--heuristic/--no-heuristic", default=True, help="Enable heuristic analysis")
@click.option("--yara/--no-yara", default=False, help="Enable YARA rules (Linux)")
@click.option("--ml", is_flag=True, help="Enable experimental ML scoring")
@click.option("--cloud", is_flag=True, help="Enable optional cloud hash lookup")
@click.option("--output", type=click.Path(), help="Write report to file")
def scan(path, quick, full, threads, heuristic, yara, ml, cloud, output):
    """
    Scan a path for known and suspicious files.

    Examples:
      python -m src.main scan .
      python -m src.main scan --quick /tmp
      python -m src.main scan /path/to/file
    """
    if full:
        scan_path = Path("/") if platform.system().lower() != "windows" else Path("C:\\")
        rprint("[yellow]Full system scan requested. This may take a long time.[/yellow]")
    elif path:
        scan_path = Path(path)
    else:
        scan_path = Path(".")

    if not scan_path.exists():
        rprint(f"[red]Path does not exist: {scan_path}[/red]")
        sys.exit(1)

    rprint(f"[cyan]Scanning: {scan_path}[/cyan]")
    rprint(f"[dim]Threads: {threads or HEXAVGConfig.DEFAULT_THREADS} | Heuristic: {heuristic} | YARA: {yara} | ML: {ml} | Cloud: {cloud}[/dim]")

    try:
        scanner = HEXAVGScanner(
            threads=threads,
            enable_heuristics=heuristic,
            enable_yara=yara,
        )
        results = scanner.scan(
            scan_path=scan_path,
            quick_scan=quick,
            dry_run=True,
        )

        threats = results.get("threats", [])
        files_scanned = results.get("files_scanned", 0)
        duration = results.get("duration", 0)

        table = Table(title="Scan Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Files scanned", str(files_scanned))
        table.add_row("Threats found", str(len(threats)))
        table.add_row("Duration (s)", f"{duration:.2f}")
        console.print(table)

        if threats:
            t = Table(title="Detections")
            t.add_column("File", style="red")
            t.add_column("Status", style="yellow")
            t.add_column("Details", style="magenta")
            for threat in threats[:50]:
                if isinstance(threat, dict):
                    path_str = str(threat.get("file_path") or threat.get("path") or threat.get("file") or "?")
                    status = str(threat.get("status", ""))
                    details = threat.get("threats") or threat.get("name") or ""
                    if isinstance(details, list):
                        details = "; ".join(
                            f"{d.get('type','?')}:{d.get('name', d)}" if isinstance(d, dict) else str(d)
                            for d in details
                        )
                    t.add_row(path_str[:60], status, str(details)[:80])
                else:
                    t.add_row("?", "?", str(threat)[:80])
            console.print(t)

        if output:
            out = Path(output)
            with out.open("w") as f:
                f.write(f"HEX-AVG Scan Report\n")
                f.write(f"Path: {scan_path}\n")
                f.write(f"Files: {files_scanned}\n")
                f.write(f"Threats: {len(threats)}\n")
                for threat in threats:
                    f.write(f"  {threat}\n")
            rprint(f"[green]Report written to {out}[/green]")

        if ml:
            try:
                get_ml_scorer()
                rprint("[dim]ML scoring is experimental and was not applied to every file in this pass.[/dim]")
            except Exception as e:
                rprint(f"[yellow]ML scoring unavailable: {e}[/yellow]")

        if cloud:
            try:
                get_cloud_client()
                rprint("[dim]Cloud lookup is optional and offline-capable.[/dim]")
            except Exception as e:
                rprint(f"[yellow]Cloud client unavailable: {e}[/yellow]")

        sys.exit(2 if threats else 0)

    except KeyboardInterrupt:
        rprint("\n[yellow]Scan interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        rprint(f"[red]Scan failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def update():
    """Check for tool / signature updates (requires network)."""
    try:
        if UpdateManager is None:
            raise RuntimeError("Update module not available")
        mgr = UpdateManager()
        info = mgr.check_for_updates()
        if info:
            rprint(f"[cyan]Update available: {info}[/cyan]")
        else:
            rprint("[green]No updates found (or offline).[/green]")
    except Exception as e:
        rprint(f"[yellow]Update check failed (offline or not configured): {e}[/yellow]")


@cli.command()
def gui():
    """Launch the experimental Tkinter GUI (if available)."""
    try:
        from src.gui.main_window import launch_gui
        rprint("[blue]Launching GUI...[/blue]")
        launch_gui()
    except Exception as e:
        rprint(f"[red]GUI unavailable: {e}[/red]")
        rprint("[dim]Tkinter may be missing or the GUI is incomplete.[/dim]")


@cli.command()
def defender():
    """Show Windows Defender coexistence information (informational only)."""
    try:
        integrator = get_defender_integrator()
        integrator.show_coexistence_notice()
        status = integrator.get_coexistence_info()
        console.print(Panel.fit(
            f"Defender status: {status.get('defender_status', 'n/a')}\n"
            f"Mode: {status.get('coexistence_mode', 'informational')}\n"
            f"HEX-AVG does not disable or modify Windows Defender.",
            title="Defender Coexistence",
        ))
    except Exception as e:
        rprint(f"[yellow]Defender integration unavailable: {e}[/yellow]")


@cli.command()
def version():
    """Show version details."""
    table = Table(title="HEX-AVG Version")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("HEX-AVG", HEXAVGConfig.VERSION)
    table.add_row("Codename", getattr(HEXAVGConfig, "VERSION_NAME", "Phoenix"))
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Platform", platform.system())
    table.add_row("Status", "Educational / Experimental")
    console.print(table)


def main():
    """Main entry point."""
    if platform.system().lower() == "windows":
        try:
            get_defender_integrator().show_coexistence_notice()
        except Exception:
            pass
    cli()


if __name__ == "__main__":
    main()
