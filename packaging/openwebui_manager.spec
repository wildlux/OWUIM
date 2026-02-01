# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file per Open WebUI Manager
"""

import sys
from pathlib import Path

block_cipher = None

# Directory base
BASE_DIR = Path(SPECPATH)

# File dati da includere
datas = [
    (str(BASE_DIR / 'scripts'), 'scripts'),
    (str(BASE_DIR / 'docs'), 'docs'),
    (str(BASE_DIR / 'tools'), 'tools'),
    (str(BASE_DIR / 'docker-compose.yml'), '.'),
    (str(BASE_DIR / 'manage.sh'), '.'),
]

# Filtra solo file esistenti
datas = [(src, dst) for src, dst in datas if Path(src).exists()]

a = Analysis(
    ['openwebui_gui.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
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
    name='OpenWebUI-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI senza console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Aggiungi icona se disponibile
)
