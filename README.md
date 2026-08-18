# HEX-AVG Antivirus

**Defensive malware detection for learning, labs, and security research.**

[![Version](https://img.shields.io/badge/version-3.0.1-blue.svg)](https://github.com/BluHExH/HEX-AVG-ANTIVIRUS)
[![Python](https://img.shields.io/badge/python-3.11%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)](#disclaimer)

HEX-AVG is an **educational / experimental** open-source antivirus written in Python.  
It is designed for cybersecurity students, malware-analysis labs, and defensive research — **not** as a replacement for commercial endpoint protection.

---

## Feature status

| Feature | Status |
|---------|--------|
| File scanning (single + directory) | **Stable** |
| SHA-256 / SHA-1 / MD5 hashing | **Stable** |
| Signature detection (hash DB + EICAR) | **Stable** |
| Multi-threaded traversal | **Stable** |
| Heuristic analysis (entropy, extensions) | Experimental |
| YARA rules | Optional (graceful if unavailable) |
| ML scoring | Experimental scaffold |
| Cloud hash lookup | Optional / offline-safe |
| CLI | **Stable** |
| GUI (Tkinter) | Experimental |
| Auto-update | Experimental |
| Windows Defender coexistence | Informational only |
| Real-time / kernel protection | **Not implemented** |

---

## Detection pipeline

```
File / Directory
       ↓
  Traversal
       ↓
   Hashing (MD5 / SHA1 / SHA256)
       ↓
 Signature Detection  →  known threats
       ↓
 Heuristic Analysis   →  suspicious patterns
       ↓
 YARA (optional)      →  rule matches
       ↓
 ML Scoring (experimental)
       ↓
 Result Aggregation  →  CLI / report
```

---

## Quick start

```bash
git clone https://github.com/BluHExH/HEX-AVG-ANTIVIRUS.git
cd HEX-AVG-ANTIVIRUS

python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### CLI

```bash
python -m src.main --help
python -m src.main --version

# Scan a path (non-destructive / dry-run style)
python -m src.main scan .
python -m src.main scan /path/to/file
python -m src.main scan --quick /tmp
```

### Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Build (PyInstaller)

```bash
pip install -r requirements-dev.txt
pyinstaller hex_avg.spec --clean --noconfirm
# Linux:  ./dist/hex-avg --version
# Windows: dist\hex-avg.exe --version
```

---

## EICAR test

HEX-AVG detects the standard **EICAR** test string (harmless). Use it to verify signature detection without real malware.

```bash
# Create EICAR test file, then:
python -m src.main scan /path/to/eicar.com
```

---

## Project layout

```
src/
  main.py              # Official entrypoint: python -m src.main
  cli.py               # Click CLI
  core/                # Scanner, hasher, traversal, threads
  detection/           # Signature, heuristic, YARA, ML
  gui/                 # Experimental Tkinter UI
tests/                 # pytest suite
signatures/            # EICAR + YARA rules
hex_avg.spec           # Single PyInstaller config
requirements.txt
requirements-dev.txt
```

---

## Security model

- Default scan behaviour is **non-destructive** (report only).
- HEX-AVG **never disables** Windows Defender.
- No hardcoded API keys or secrets are required for local scanning.
- Cloud features (if used) send **hashes only**, never file contents.
- Do not test with real malware on production hosts — use isolated VMs and EICAR.

---

## Limitations

HEX-AVG does **not** provide:

- Kernel / rootkit detection  
- Fileless / in-memory malware coverage  
- Network traffic analysis  
- Real-time filesystem monitoring  
- Enterprise policy management  

---

## Disclaimer

**HEX-AVG is an educational and experimental defensive security project.**  
It is **not** a replacement for a mature commercial or enterprise endpoint security product.  
The authors are not responsible for misuse or for damage caused by relying on this tool as a sole security control.

---

## License

No license file is present in the repository yet. The owner should add a license before redistribution.

---

## Contributing

Issues and pull requests are welcome. Prefer small, tested changes. Keep the project educational and defensive.

**Version:** 3.0.1 · **Codename:** Phoenix Rising
