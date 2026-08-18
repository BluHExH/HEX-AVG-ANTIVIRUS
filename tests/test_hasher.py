"""Tests for FileHasher."""
import hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.hasher import FileHasher


def test_hash_known_content(tmp_path):
    data = b"HEX-AVG test content"
    f = tmp_path / "sample.txt"
    f.write_bytes(data)
    hasher = FileHasher()
    result = hasher.hash_file(f)
    assert result["md5"] == hashlib.md5(data).hexdigest()
    assert result["sha1"] == hashlib.sha1(data).hexdigest()
    assert result["sha256"] == hashlib.sha256(data).hexdigest()


def test_hash_missing_file(tmp_path):
    hasher = FileHasher()
    missing = tmp_path / "nope.bin"
    try:
        hasher.hash_file(missing)
        assert False, "should raise"
    except FileNotFoundError:
        pass
