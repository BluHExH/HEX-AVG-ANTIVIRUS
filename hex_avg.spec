# -*- mode: python ; coding: utf-8 -*-
# HEX-AVG PyInstaller spec — single official build config

block_cipher = None

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("signatures", "signatures"),
        ("config.py", "."),
    ],
    hiddenimports=[
        "src.cli",
        "src.core.scanner",
        "src.core.file_traversal",
        "src.core.hasher",
        "src.core.multithreading",
        "src.detection.signature",
        "src.detection.heuristic",
        "src.detection.advanced_heuristic",
        "src.detection.ml_scoring",
        "src.detection.yara_engine",
        "src.detection.persistence",
        "src.update.update_manager",
        "src.cloud.cloud_sync",
        "src.defender_integration",
        "src.gui.main_window",
        "config",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="hex-avg",
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
