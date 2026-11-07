# WinStorePackager — Windows Store Build-Anleitung

Stand: 2026-11-07 (Tier-2 6-Sprachen Store-Readiness)

## Voraussetzungen

1. Python 3.10+ mit Tkinter (Standard)
2. PyInstaller (`pip install pyinstaller`)
3. Windows SDK (für `makeappx.exe` und `signtool.exe`)
4. Code-Signing-Zertifikat (.pfx) für MSIX-Signierung
5. Microsoft Store Entwicklerkonto (Partner Center)

## Schritt 1: EXE bauen

**WICHTIG:** IMMER über `build_exe.bat` / `WinStorePackager.spec` bauen —
NICHT über einen freien `pyinstaller --onefile --windowed ...`-Aufruf ohne
Spec-Datei. Grund: Ein Build ohne die `hiddenimports` aus der Spec-Datei hat `keyring` nicht gebündelt.

```bash
cd "<PROJECT_ROOT>"
build_exe.bat
```

Das Skript installiert `requirements.txt` + `pyinstaller` im Build-Interpreter
und baut anschließend `WinStorePackager.spec` (die Spec-Datei enthält die
`hiddenimports` für `keyring`, dessen Windows-Backend/`win32ctypes`, `PIL` und
`pygetwindow`). Ergebnis: `dist\WinStorePackager.exe`.

## Schritt 2: Store-Paket vorbereiten

```bash
mkdir store_package
copy dist\WinStorePackager.exe store_package\
xcopy store_assets store_package\icons\ /E
copy LICENSE store_package\
```

Lokale Readiness ohne Store-SDK/Adminrechte:

```powershell
python -m pytest -q tests\test_self_dogfood_profile.py tests\test_store_dogfood_readiness.py
```

## Schritt 3: MSIX bauen (Dogfooding — Tool mit sich selbst packen!)

1. WinStorePackager starten
2. Eigenes Projektprofil `winstorepackager-project-v1.json` importieren oder Settings aus `releases/windowsstore/store_settings.json` laden
3. Publisher-ID aus dem Partner Center lokal eintragen
4. MSIX bauen und signieren
5. Danach `releases/WinStorePackager.msix` gegen `releases/windowsstore/WACK_PROTOCOL.md` prüfen

## Schritt 4: Store Submission

1. Partner Center öffnen: https://partner.microsoft.com/dashboard
2. Neue App erstellen / reservierte App auswählen (Store-ID `9NT273Z50BJR`)
3. MSIX-Paket hochladen
4. Store-Listing aus den 6 Zielsprachen (`store_listing_de.md`, `store_listing_en.md`, `store_listing_es.md`, `store_listing_zh.md`, `store_listing_ja.md`, `store_listing_ru.md`) übertragen
5. Preis: KOSTENLOS
6. Submission absenden
