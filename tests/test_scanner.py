"""Tests for HEXAVGScanner."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.scanner import HEXAVGScanner

EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def test_scan_clean_file(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text("hello")
    scanner = HEXAVGScanner(threads=2, enable_heuristics=True, enable_yara=False)
    results = scanner.scan(f, dry_run=True)
    assert results["files_scanned"] >= 1
    assert results["threats_found"] == 0 or len(results.get("threats", [])) == 0


def test_scan_eicar(tmp_path):
    f = tmp_path / "eicar.com"
    f.write_bytes(EICAR)
    scanner = HEXAVGScanner(threads=2, enable_heuristics=False, enable_yara=False)
    results = scanner.scan(f, dry_run=True)
    assert results["threats_found"] >= 1 or len(results.get("threats", [])) >= 1


def test_scan_missing_path():
    scanner = HEXAVGScanner(threads=1)
    try:
        scanner.scan(Path("/nonexistent/path/xyz"), dry_run=True)
        assert False
    except FileNotFoundError:
        pass
