# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get HEX-AVG configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HEXAVGConfig

block_cipher = None

a = Analysis(
    ['hex_avg.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('signatures', 'signatures'),
        ('config.py', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'src.core.scanner',
        'src.core.file_traversal',
        'src.core.hasher',
        'src.core.multithreading',
        'src.detection.signature',
        'src.detection.heuristic',
        'src.detection.yara_engine',
        'src.detection.persistence',
        'click',
        'rich',
        'tqdm',
        'psutil',
        'yara',
        'pyelftools',
        'cryptography',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hex-avg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Create a portable directory structure
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hex-avg-linux',
)

# Additional files for portable package
import shutil
portable_dir = Path('dist/hex-avg-linux')
(portable_dir / 'README.txt').write_text('''
HEX-AVG Antivirus - Linux Portable Version
===========================================

QUICK START:
1. Open terminal
2. Navigate to this directory
3. Run: ./hex-avg scan --quick
   Or: sudo ./hex-avg scan /

FEATURES:
- Manual virus scanning
- Signature-based detection
- Heuristic analysis
- YARA rule support
- Custom scan paths
- Quarantine management

REQUIREMENTS:
- Linux kernel 3.10+
- Python 3.11+ (bundled)
- No installation required for portable version
- For full features, run as root or with sudo

DOCUMENTATION:
Full documentation available at: https://github.com/yourusername/hex-avg

SUPPORT:
Report issues at: https://github.com/yourusername/hex-avg/issues
''')

(portable_dir / 'LICENSE').write_text((Path(__file__).parent.parent / 'LICENSE').read_text() if (Path(__file__).parent.parent / 'LICENSE').exists() else 'MIT License')