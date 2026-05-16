# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Repo-Hygiene-Check vom 2026-05-17 in README und Projektlog dokumentiert.
- `.gitattributes` ergänzt, damit Text- und Binärdateien konsistent behandelt werden.
- README bindet jetzt den vorhandenen GUI-Screenshot aus `README/screenshots/main.png` direkt ein.
- Lokales EXE-Bundle wird in `releases/v2.3.0/` aus dem aktuellen `dist/WinStorePackager.exe` gepflegt.
- `RELEASES.md` dokumentiert den lokalen Release-Artefakt-Workflow.

### Geändert / Changed
- Deutsche Endnutzertexte nutzen echte Umlaute statt Umschreibungen.
- `.gitignore` deckt zusätzliche Store-, Signier- und WACK-Artefakte ab.
- Lokale Release-Artefakte werden inklusive Source-ZIP und SHA256-Datei versioniert abgelegt.
- README, SECURITY und CONTRIBUTING verweisen jetzt auf `file-bricks/WinStorePackager`.
- `START.bat` setzt UTF-8 und nutzt bevorzugt `py -3`.

### Behoben / Fixed
- Persönliche Kontaktadresse aus dem Code of Conduct entfernt.
- `_WARTUNG/` und lokale Build-/Staging-Artefakte werden nicht mehr im Git-Index geführt.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
