# -*- mode: python ; coding: utf-8 -*-
"""
HEX-AVG PyInstaller Specification File
=======================================

This spec file configures PyInstaller to build HEX-AVG into a single
executable for Windows and Linux distributions.

Key Features:
- Single executable distribution
- All dependencies bundled
- Data files included (signatures, models)
- Hidden imports declared for all modules
- Cross-platform compatibility
"""

import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

block_cipher = None
NAME = "hex-avg"
VERSION = "3.0.0"

# ============================================================================
# DATA FILES TO INCLUDE
# ============================================================================

datas = [
    # Virus signatures (mandatory)
    ('signatures', 'signatures'),
    
    # Configuration file
    ('config.py', '.'),
]

# Add models directory if it exists
models_dir = Path('models')
if models_dir.exists() and any(models_dir.iterdir()):
    datas.append(('models', 'models'))

# Add GUI resources if they exist
gui_resources = Path('src/gui/resources')
if gui_resources.exists() and any(gui_resources.iterdir()):
    for resource_file in gui_resources.iterdir():
        if resource_file.is_file():
            datas.append((str(resource_file), 'src/gui/resources'))

# ============================================================================
# HIDDEN IMPORTS
# ============================================================================

# PyInstaller cannot auto-detect these imports, so we declare them explicitly
hiddenimports = [
    # Core modules
    'src.core.scanner',
    'src.core.file_traversal',
    'src.core.hasher',
    'src.core.multithreading',
    
    # Detection engines
    'src.detection.signature',
    'src.detection.heuristic',
    'src.detection.advanced_heuristic',
    'src.detection.ml_scoring',
    'src.detection.yara_engine',
    'src.detection.persistence',
    
    # Services & monitoring (LEVEL-2 features)
    'src.services.windows_service',
    'src.services.linux_daemon',
    'src.monitoring.windows_monitor',
    'src.monitoring.linux_monitor',
    'src.scheduler.scan_scheduler',
    
    # New v3.0.0 features
    'src.update.update_manager',
    'src.cloud.cloud_sync',
    'src.gui.main_window',
    'src.defender_integration',
    
    # Third-party libraries (often not auto-detected)
    'click',
    'click.core',
    'click.formatting',
    'rich',
    'rich.console',
    'rich.table',
    'rich.progress',
    'tqdm',
    'psutil',
    'yara',
    'yara-python',
    'pefile',
    'elftools',
    'cryptography',
    'yaml',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',
    'schedule',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    
    # Protocol buffers (used by some libraries)
    'google.protobuf',
    
    # dateutil
    'dateutil',
    'dateutil.parser',
]

# ============================================================================
# EXCLUDES (Reduce Binary Size)
# ============================================================================

excludes = [
    # Data science libraries (not needed for antivirus)
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    
    # Development tools
    'IPython',
    'jupyter',
    'pytest',
    'black',
    'flake8',
    'mypy',
    
    # Documentation
    'sphinx',
    'docutils',
]

# ============================================================================
# PYINSTALLER ANALYSIS
# ============================================================================

a = Analysis(
    ['src/main.py'],  # Single entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ============================================================================
# PYINSTALLER ARCHIVES
# ============================================================================

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ============================================================================
# EXECUTABLE CONFIGURATION
# ============================================================================

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for CLI interface
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ============================================================================
# PLATFORM-SPECIFIC CONFIGURATION
# ============================================================================

# Windows icon (if exists)
if Path('build/windows/icon.ico').exists():
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=NAME,
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
        icon='build/windows/icon.ico',
    )

# Linux icon (if exists)
elif Path('build/linux/icon.png').exists():
    # Note: PyInstaller doesn't support setting icons for Linux binaries directly
    # Icons are typically set via .desktop files for Linux
    pass