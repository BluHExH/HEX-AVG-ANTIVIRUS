"""Tests for SignatureDetector with EICAR."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.hasher import FileHasher
from src.detection.signature import SignatureDetector

EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def test_eicar_detected(tmp_path):
    f = tmp_path / "eicar.com"
    f.write_bytes(EICAR)
    hasher = FileHasher()
    hashes = hasher.hash_file(f)
    det = SignatureDetector()
    result = det.detect(f, hashes)
    assert result["detected"] is True
    assert "EICAR" in (result.get("name") or "")


def test_clean_file_not_detected(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text("just a clean text file for testing")
    hasher = FileHasher()
    hashes = hasher.hash_file(f)
    det = SignatureDetector()
    result = det.detect(f, hashes)
    assert result["detected"] is False
