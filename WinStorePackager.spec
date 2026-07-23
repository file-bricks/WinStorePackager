# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# WELLE-1-USERTEST U1 (2026-07-23): keyring wurde bislang NICHT gebuendelt
# (leeres hiddenimports=[]) -- PyInstallers Static-Import-Analyse erkennt
# keyrings Backend-Discovery (entry_points, Windows-Backend ueber
# pywin32-ctypes/win32ctypes) nicht zuverlaessig, ebenso wenig den
# try/except-Import-Block in WindowsStorePublisher_3.py. Folge war
# "ModuleNotFoundError: No module named 'keyring'" beim Start der Frozen-EXE.
# collect_submodules() statt einzelner Namen, damit neue Backend-Module
# (z. B. bei keyring-Updates) nicht erneut vergessen werden.
_hiddenimports = (
    collect_submodules('keyring')
    + collect_submodules('win32ctypes')
    + [
        'PIL',
        'PIL.Image',
        'PIL.ImageGrab',
        'pygetwindow',
    ]
)

a = Analysis(
    ['WindowsStorePublisher_3.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WinStorePackager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['WinStorePackager.ico'],
)
