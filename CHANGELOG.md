# Changelog

## 3.0.1 — 2026-08-17

### Fixed
- Single official entrypoint: `python -m src.main`
- Broken string literals (HTML-escaped quotes) in CLI and persistence modules
- Signature detector never initialized in scanner (EICAR was not detected)
- SQLite thread-safety for multi-threaded scans
- Single-file scan support (previously directories only)
- CLI imports mismatched real class names (`HEXAVGScanner`, `SignatureDetector`, …)
- `requirements.txt` no longer lists stdlib modules (`sqlite3`, `hashlib`)

### Added
- Real pytest suite (hasher, signature, scanner, heuristic, CLI)
- `requirements-dev.txt`
- Honest README describing educational/experimental status
- Clean CI and release GitHub Actions workflows

### Removed / cleaned (intended)
- Competing top-level entrypoints (`hex_avg.py`, `hex_avg_level2.py`, `hex_avg_v3.py`, `build.py`)
- Legacy `build/` directory and duplicate specs
- Unrelated Azure Functions workflow
- Redundant AI-generated summary markdown files

### Notes
- Version bumped to 3.0.1
- Project is educational/experimental — not production antivirus
