# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Sichtbare Anwendungssprache Deutsch/Englisch unter "Build-Einstellungen"
  (Combobox, persistiert in `settings_store_packager.json`, nutzt
  `translator.py`/`locales/translations.json`). Fenstertitel und Reiter
  werden sofort neu übersetzt; die übrigen GUI-Texte wirken nach einem
  Neustart vollständig (WELLE-1-USERTEST U2, 2026-07-23).
- `tests/test_language_switch.py` deckt Persistenz, Reload und sichtbares
  Combobox-Widget der Sprachumschaltung ab.
- `tests/test_frozen_guard.py` deckt den Frozen-Guard in `install_and_import`
  (kein Laufzeit-pip-Fallback, kein `input()` in einer Frozen-EXE) sowie die
  `hiddenimports` in `WinStorePackager.spec` ab.
- `tests/pretest_exe_startup.py`: eigenständiger Pretest, der die reale
  gebaute EXE startet und die Prozesszahl überwacht (Fork-Bomben-Erkennung) --
  schließt die Lücke, dass der bisherige Pretest nur den Python-Quellimport
  prüfte und den Startcrash der Frozen-EXE nicht fing.
- `winstorepackager-project-v1.json` als eigenes Self-Dogfooding-Profil ergänzt; es enthält Store-Metadaten, Projektpfade und Listing-Kontext ohne Publisher-DN, SDK-Pfade oder Zertifikatsdaten.
- `tests/test_self_dogfood_profile.py` validiert das eigene Projektprofil gegen `store_package.json`, prüft sensible Felder und führt den SDK-freien Preflight mit dem Profil aus.
- `generate_store_screenshots.py` erzeugt ein kuratiertes Microsoft-Store-Screenshot-Set mit vier 1920x1080-PNGs ohne Publisher-, Zertifikats- oder Privatpfad-Daten.
- `tests/test_store_screenshots.py` prüft Dateinamen, PNG-Format, Abmessungen und Nicht-Leerheit des generierten Store-Screenshot-Sets.
- `unix_preflight.py` ergänzt: SDK-freier Unix-Preflight (für Linux und macOS) prüft Projektstruktur, `store_package.json`, README, Privacy Policy, Store-Listing, Screenshot-/Icon-Artefakte und optional exportierte Projektprofile.
- `tests/test_unix_preflight.py` deckt gültige Unix-Preflights, fehlende Artefakte, Drift zwischen Projektprofil und Store-Metadaten sowie den Abwärtskompatibilitäts-Wrapper ab.
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
- README und README_de dokumentieren den Self-Dogfooding-Einstieg über `winstorepackager-project-v1.json`.
- `.gitignore` erlaubt nur die kuratierten Demo-Store-Screenshots unter `releases/windowsstore/screenshots/*.png`; andere Release-, Paket-, Signier- und WACK-Artefakte bleiben ignoriert.
- README.md verlinkt jetzt die neue deutsche README_de.md; README_de.md ergänzt eine deutschsprachige Nutzerführung für Microsoft-Store-/MSIX-Vorbereitung.
- `llms.txt` verweist auf README_de.md und trägt `Last-checked: 2026-06-12`.
- `PORTIERUNGSPLAN.md`, `AUFGABEN.txt` und README führen den Linux- und macOS-Preflight jetzt als erledigte P3-Desktop-Schritte; der macOS-Preflight wurde mit dem Linux-Preflight in `unix_preflight.py` zusammengeführt (mit `linux_preflight.py` als Abwärtskompatibilitäts-Wrapper).
- README-Einstieg, Suchphrasen und Discoverability-Kontext für Python-Microsoft-Store-/MSIX-Packaging geschärft.
- Deutsche Endnutzertexte nutzen echte Umlaute statt Umschreibungen.
- `.gitignore` deckt zusätzliche Store-, Signier- und WACK-Artefakte ab.
- `START.bat` bevorzugt jetzt die lokal gebaute `dist\WinStorePackager.exe`; `build_exe.bat` und `WinStorePackager.spec` dokumentieren den reproduzierbaren lokalen PyInstaller-Build.
- Lokale Release-Artefakte werden inklusive Source-ZIP und SHA256-Datei versioniert abgelegt.
- README, SECURITY und CONTRIBUTING verweisen jetzt auf `file-bricks/WinStorePackager`.
- `START.bat` setzt UTF-8 und nutzt bevorzugt `py -3`.

### Behoben / Fixed
- **KRITISCH (WELLE-1-USERTEST U1, 2026-07-23):** Release-EXE v2.3.0 stürzte
  beim Start ab (`ModuleNotFoundError: No module named 'keyring'`, danach
  `RuntimeError: lost sys.stdin`), weil `WinStorePackager.spec` keine
  `hiddenimports` für `keyring` (inkl. Windows-Backend/`win32ctypes`) enthielt
  und PyInstaller das Modul daher nicht bündelte. Der anschließende
  Laufzeit-pip-Fallback in `install_and_import()` wirkte in der Frozen-EXE
  zusätzlich als FORK-BOMBE, da `sys.executable` dort auf die EXE selbst
  zeigt (`sys.executable -m pip install ...` startet die App erneut statt
  pip; real 491 Prozesse). Fix: `WinStorePackager.spec` bündelt jetzt
  `keyring`/`win32ctypes` über `collect_submodules()`; `install_and_import()`
  installiert in Frozen-Builds (`sys.frozen`) ersatzlos nichts mehr nach,
  sondern zeigt einen Fehlerdialog (`_fatal_missing_module_frozen`) und
  beendet sich sauber ohne `input()`/`subprocess`. `build_exe.bat`
  installiert `requirements.txt` jetzt vor jedem Build im Build-Interpreter,
  damit PyInstaller neue Abhängigkeiten überhaupt bündeln kann.
- `web_companion`: Icon-Uploads werden für die Vorschau nur noch als PNG/JPG/WebP
  akzeptiert und über `createImageBitmap` plus Canvas gerendert, statt einen
  Datei-Object-URL direkt an `img.src` zu übergeben.
- Projektprofil-Export bricht bei absoluten Pfaden auf unterschiedlichen Windows-Laufwerken nicht mehr mit `ValueError` ab; in diesem Fall bleiben die Pfade bewusst absolut.
- `.gitignore` ist wieder UTF-8 ohne BOM und entfernt interne Planungsdateien aus dem öffentlichen Git-Tracking.
- Persönliche Kontaktadresse aus dem Code of Conduct entfernt.
- `_WARTUNG/` und lokale Build-/Staging-Artefakte werden nicht mehr im Git-Index geführt.
- `web_companion`: 6 PWA-Bugs behoben — `exportProfile` hängt Link vor Click in den DOM ein und entfernt ihn danach (iOS-Safari/Firefox-Kompatibilität), `persistToStorage` fängt `localStorage.setItem`-Fehler im Safari-Private-Mode ab, `installApp` nullt `deferredInstallPrompt` vor `prompt()` (Doppel-Trigger verhindert), `service-worker.js` schließt alle 4 Icons in `APP_SHELL` ein, `apple-touch-icon` zeigt auf `Icon-192.png` (non-maskable), `manifest.webmanifest` setzt `purpose: any` für nicht-maskierbare Icons; 13/13 Regressionstests grün.
- `unix_preflight._validate_store_package`: Fehlendes oder leeres `executable`-Feld wurde fälschlicherweise als „muss auf `.exe` enden" gemeldet statt als „fehlt"; Prüfung konsistent mit den anderen Pflichtfeldern gemacht (leeres Feld → „fehlt", nicht-leeres ohne .exe → „muss auf .exe enden").

### CI
- `test_project_profile.py` nutzt für den relativen Projektpfad-Test jetzt einen plattformneutralen temporären Projektroot, damit derselbe Test unter Windows, Linux und macOS gültig ist.
- `source-platform-smoke` setzt jetzt `PYTHONPATH` auf das Repo-Root, damit die Root-Module `linux_preflight.py` und `project_profile.py` auf Ubuntu- und macOS-Runnern importierbar sind.
- `source-platform-smoke` Workflow ergänzt: führt `test_unix_preflight.py` und `test_project_profile.py` (8 Tests, stdlib-only) auf `ubuntu-latest` und `macos-latest` mit Python 3.11 aus und validiert so die SDK-freie Unix-Projektstruktur und Profil-Roundtrips.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
