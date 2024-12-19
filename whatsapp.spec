# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

# Collect all required data files and metadata
datas = []
datas += collect_data_files('emoji')
datas += collect_data_files('wordcloud')
datas += collect_data_files('matplotlib')
datas += copy_metadata('emoji')
datas += copy_metadata('pandas')
datas += copy_metadata('numpy')
datas += copy_metadata('matplotlib')

# Collect all required imports
hiddenimports = [
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.dtypes',
    'pandas._libs.tslibs.timezones',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_svg',
    'numpy',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.scrolledtext',
    'PIL',
    'PIL._tkinter_finder',
    'emoji.core',
    'wordcloud',
]

# Add matplotlib backends
hiddenimports += collect_submodules('matplotlib.backends')
hiddenimports += collect_submodules('matplotlib.pyplot')
hiddenimports += collect_submodules('numpy')

a = Analysis(
    ['whatsapp_analyzer_gui.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate binaries and data files
a.binaries = list(set(a.binaries))
a.datas = list(set(a.datas))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WhatsAppAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide the console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    onefile=True  # Create a single file executable
) 