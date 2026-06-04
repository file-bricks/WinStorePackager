@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set BUILD_ROOT=C:\_Local_DEV\codex_build\winstorepackager

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m PyInstaller --noconfirm --workpath "%BUILD_ROOT%\build" --distpath "%cd%\dist" WinStorePackager.spec
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden.
        pause
        exit /b 1
    )
    python -m PyInstaller --noconfirm --workpath "%BUILD_ROOT%\build" --distpath "%cd%\dist" WinStorePackager.spec
)

if errorlevel 1 (
    echo [FEHLER] EXE-Build fehlgeschlagen.
    pause
    exit /b 1
)

echo [OK] dist\WinStorePackager.exe wurde erstellt.
