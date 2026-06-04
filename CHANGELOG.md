# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- `llms.txt` als maschinenlesbarer Projektkontext für Crawler, LLMs und Repo-Navigation ergänzt.
- `PORTIERUNGSPLAN.md` ergänzt: Windows Store bleibt Hauptkanal, Web/PWA wird Companion-Linie, Android/iOS nur PWA-Testziel, macOS/Linux nur SDK-freier Preflight.
- Projektaufgaben um P0-P3-Portierungsschritte für Dogfooding, Austauschformat `winstorepackager-project-v1.json`, Web/PWA und Preflight ergänzt.
- `PROJECT_PROFILE_FORMAT.md` dokumentiert jetzt das gemeinsame Austauschformat `winstorepackager-project-v1.json`.
- Desktop-App kann Projektprofile jetzt sicher importieren und exportieren, ohne Publisher-ID, SDK-Pfade oder Zertifikatsdaten mitzuschreiben.
- `web_companion/` als lokaler Browser-Companion für Manifest-Vorschau, Icon-Check und JSON-Import/Export ergänzt.
- `web_companion/` ist jetzt als installierbare PWA nutzbar: `service-worker.js`, `offline.html`, `icon.svg` und `serve_companion.py` ergänzen Offline-Shell, Install-Flow und localhost-Start.
- `tests/test_project_profile.py` deckt Profil-Serialisierung und Pfadauflösung ab.
- Repo-Hygiene-Check vom 2026-05-17 in README und Projektlog dokumentiert.
- `.gitattributes` ergänzt, damit Text- und Binärdateien konsistent behandelt werden.
- README bindet jetzt den vorhandenen GUI-Screenshot aus `README/screenshots/main.png` direkt ein.
- Lokales EXE-Bundle wird in `releases/v2.3.0/` aus dem aktuellen `dist/WinStorePackager.exe` gepflegt.
- `RELEASES.md` dokumentiert den lokalen Release-Artefakt-Workflow.

### Geändert / Changed
- README-Einstieg, Suchphrasen und Discoverability-Kontext für Python-Microsoft-Store-/MSIX-Packaging geschärft.
- Deutsche Endnutzertexte nutzen echte Umlaute statt Umschreibungen.
- `.gitignore` deckt zusätzliche Store-, Signier- und WACK-Artefakte ab.
- `START.bat` bevorzugt jetzt die lokal gebaute `dist\WinStorePackager.exe`; `build_exe.bat` und `WinStorePackager.spec` dokumentieren den reproduzierbaren lokalen PyInstaller-Build.
- Lokale Release-Artefakte werden inklusive Source-ZIP und SHA256-Datei versioniert abgelegt.
- README, SECURITY und CONTRIBUTING verweisen jetzt auf `file-bricks/WinStorePackager`.
- `START.bat` setzt UTF-8 und nutzt bevorzugt `py -3`.

### Behoben / Fixed
- Projektprofil-Export bricht bei absoluten Pfaden auf unterschiedlichen Windows-Laufwerken nicht mehr mit `ValueError` ab; in diesem Fall bleiben die Pfade bewusst absolut.
- `.gitignore` ist wieder UTF-8 ohne BOM und entfernt interne Planungsdateien aus dem öffentlichen Git-Tracking.
- Persönliche Kontaktadresse aus dem Code of Conduct entfernt.
- `_WARTUNG/` und lokale Build-/Staging-Artefakte werden nicht mehr im Git-Index geführt.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
