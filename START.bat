@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

where py >nul 2>&1
if not errorlevel 1 (
    py -3 "WindowsStorePublisher_3.py"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden.
        pause
        exit /b 1
    )
    python "WindowsStorePublisher_3.py"
)

if errorlevel 1 pause
