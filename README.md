# HEX-AVG Antivirus v3.0.1

**Educational / experimental defensive antivirus** written in Python.

This is **not** a production or commercial antivirus product. It is intended for:

- Cybersecurity education
- Learning how signature and heuristic scanners work
- Lab environments and defensive tooling experiments

## Features (honest status)

| Feature | Status |
|---------|--------|
| Signature scanning (hash DB + EICAR) | Working |
| Basic heuristics (entropy, extensions) | Working |
| CLI (`scan`, `version`, `update`, …) | Working |
| Multi-threaded file scan | Working |
| YARA rules | Optional (graceful if unavailable) |
| ML scoring | Experimental scaffold |
| Cloud hash lookup | Optional / offline-safe |
| GUI (Tkinter) | Experimental |
| Windows Defender coexistence | Informational only (never disables Defender) |
| Real-time protection | Not implemented |
| Kernel / memory scanning | Not supported |

## Requirements

- Python 3.11+
- See `requirements.txt`

Optional: `yara-python` (may fail to install on some platforms; scanner continues without it).

## Quick start

```bash
# From repository root
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Help / version
python -m src.main --help
python -m src.main --version

# Scan a path (dry-run style; educational)
python -m src.main scan .
python -m src.main scan /path/to/file
python -m src.main scan --quick /tmp
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Packaging (PyInstaller)

```bash
pip install -r requirements-dev.txt
pyinstaller hex_avg.spec --clean --noconfirm
# Linux: ./dist/hex-avg --version
# Windows: dist\hex-avg.exe --version
```

## Project layout

```
src/
  main.py          # Official entrypoint (python -m src.main)
  cli.py           # Click CLI
  core/            # Scanner, hasher, traversal, threads
  detection/       # Signature, heuristic, YARA, ML
  ...
tests/             # pytest suite
signatures/        # EICAR + YARA rules
hex_avg.spec       # Single PyInstaller config
requirements.txt
requirements-dev.txt
```

## Security notes

- Default behaviour is non-destructive (scan / report).
- Do not disable your real antivirus to "make room" for this tool.
- Never test with real malware on a production host; use isolated VMs and the EICAR test file only.
- No hardcoded API keys or secrets are required for local scanning.

## License

See `LICENSE` if present. If none is present, the repository owner must choose a license before redistribution.

## Disclaimer

HEX-AVG is provided for educational purposes. The authors are not responsible for misuse or for any damage caused by reliance on this tool as a sole security control.
