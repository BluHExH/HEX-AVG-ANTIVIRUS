"""CLI smoke tests."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from click.testing import CliRunner
from src.cli import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.output.lower() or "Usage" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "3.0" in result.output or "HEX-AVG" in result.output
