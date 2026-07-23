@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set BUILD_ROOT=C:\_Local_DEV\codex_build\winstorepackager

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"

where py >nul 2>&1
if not errorlevel 1 (
    set PYCMD=py -3
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden.
        pause
        exit /b 1
    )
    set PYCMD=python
)

rem WELLE-1-USERTEST U1 (2026-07-23): requirements.txt MUSS im Build-Interpreter
rem installiert sein, bevor PyInstaller laeuft -- sonst kann PyInstaller ein
rem Modul (z. B. keyring) nicht bundeln, obwohl das Skript es importiert
rem (Root-Cause des Startcrashs "ModuleNotFoundError: No module named 'keyring'").
%PYCMD% -m pip install --quiet --disable-pip-version-check -r requirements.txt pyinstaller
if errorlevel 1 (
    echo [FEHLER] Build-Abhaengigkeiten ^(requirements.txt / pyinstaller^) konnten nicht installiert werden.
    pause
    exit /b 1
)

%PYCMD% -m PyInstaller --noconfirm --workpath "%BUILD_ROOT%\build" --distpath "%cd%\dist" WinStorePackager.spec

if errorlevel 1 (
    echo [FEHLER] EXE-Build fehlgeschlagen.
    pause
    exit /b 1
)

echo [OK] dist\WinStorePackager.exe wurde erstellt.
