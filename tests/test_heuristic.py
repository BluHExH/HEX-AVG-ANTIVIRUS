"""Heuristic engine should not crash on normal files."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.detection.heuristic import HeuristicDetector


def test_heuristic_clean_text(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("normal document content " * 20)
    det = HeuristicDetector()
    result = det.analyze(f)
    assert isinstance(result, dict)
    assert "suspicious" in result or "threats" in result
