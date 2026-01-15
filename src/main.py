#!/usr/bin/env python3
"""
HEX-AVG - Single Entry Point
===========================

This is the ONLY file PyInstaller uses as the entrypoint.
All CLI logic is implemented in src/cli.py

Usage:
    python src/main.py scan --quick
    python src/main.py scan /path/to/scan
    python src/main.py update
    python src/main.py gui
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())