# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Behoben / Fixed (2026-08-10)

Vier Fehler in der MSIX-Erzeugung, die allesamt **still** defekte Pakete
erzeugten — sie fallen erst beim Store-Upload oder beim Endnutzer auf. Gefunden
bei der Store-Einreichung von ProfiPrompt und PromptBoard, wo dieselben Muster
im CLI-Zwilling `_STORE/store_packager.py` auftraten.

- **Ordner-Builds verloren ihre Laufzeit.** Kopiert wurde nur die gewählte
  Datei. Bei PyInstaller-`--onedir` liegen Python-Laufzeit und Bibliotheken
  daneben in `_internal/`; ohne sie installiert sich die App, startet aber
  nicht. Neue Methode `stage_payload()` nimmt in diesem Fall den ganzen Ordner.
- **Dem Manifest fehlte die `<Resources>`-Sektion.** Ohne deklarierte Sprache
  löst der Store `DisplayName`, `PublisherDisplayName` und die Logos nicht auf
  und meldet sie als leer bzw. „not found" — obwohl sie im Manifest stehen. Das
  erzeugt mehrere irreführende Folgefehler. Sprache über `DEFAULT_LANGUAGES`
  (Vorgabe `en-us`) bzw. eine optionale `languages`-Variable.
- **Eingeschränkte Fähigkeiten standen im falschen Namensraum.** `runFullTrust`
  als schlichtes `<Capability>` lässt `makeappx` das gesamte Manifest ablehnen.
  Fähigkeiten werden jetzt nach Namensraum getrennt (`Capability`,
  `uap:Capability`, `rescap:Capability`).
- **Das Paket packte sich selbst ein.** Das MSIX entsteht in dem Verzeichnis,
  das verpackt wird; beim zweiten Build wanderte das Paket des Vorlaufs hinein
  und die Größe verdoppelte sich (im CLI-Zwilling gemessen: 46 → 92 MB). Eine
  vorhandene gleichnamige Datei wird jetzt vor dem Packen entfernt.

### Hinzugefügt / Added (2026-08-10)
- Vier Regressionstests in `tests/test_bugsweep_resweep_20260622.py` zu den
  obigen Punkten (Sprach-Ressourcen, `rescap`-Namensraum, Ordner- und
  Einzeldatei-Staging).

### Geändert / Changed (2026-08-03)
- UX-/Accessibility-Review: Der Changelog-Formatierungsfluss im Store-Tab nutzt jetzt echte deutsche Umlaute (`Format für Store`, `für Store-Listing`) statt der Umschreibung `fuer`.

### Geändert / Changed (2026-08-01)
- Discoverability, README-Design & SEO Check (Pfad B): Ecosystem (`file-bricks`) & Umbrella (`open-bricks`) Shields.io-Badges in `README.md` ergänzt.
- `llms.txt` Header auf `Last-checked: 2026-08-01` aktualisiert.
- Repository Hygiene Zeitstempel in `README.md` auf 2026-08-01 nachgeführt.
### TASKSOLVER verification (2026-08-10)
- Der aktuelle Projektprofilvertrag wurde erneut gegen den Desktop-/SDK-freien Pfad
  gelesen: 19 fokussierte Profil-/Preflight-/Source-Smoke-Tests bestanden, ein
  optionaler WACK-Test mangels lokalem Protokoll übersprungen.
- Der vollständige lokale Lauf besteht mit 60 Tests; sechs Tests bleiben wegen
  bewusst lokaler Store-/WACK-Artefakte bzw. fehlendem Tk-Display übersprungen.
  `python unix_preflight.py --project-root . --profile-path
  winstorepackager-project-v1.json` meldet „Keine Befunde“ und 12 geprüfte Artefakte.
- Der direkte Desktop↔Web-Import/Export-Test bleibt offen: `web_companion/` wurde
  in Commit `05705f9` entfernt und im aktuellen Checkout existiert kein autorisierter
  Web-Client. Es wurde kein Ersatz-Client erfunden oder angelegt; Task 1431 bleibt offen.

### TASKSOLVER verification (2026-08-08)
- Der Profilvertrag wird jetzt mit einem vollständigen
  `write -> read -> serialize`-Roundtrip getestet. Windows-Laufwerkspfade aus
  exportierten Profilen bleiben beim Import auf POSIX-Systemen opaque, statt
  fälschlich unter dem Profilverzeichnis rebased zu werden.
- `unix_preflight.py` ist nativ und in WSL Ubuntu mit dem Self-Dogfood-Profil
  fehler- und warnungsfrei gelaufen; der Linux-Kompatibilitätswrapper meldet
  ebenfalls `ok: true`. Der WSL-Compile-Check war erfolgreich.
- Der lokale Pytest-Lauf bestand mit 59 Tests; 7 Tests wurden wegen fehlender
  lokaler Store-/MSIX-/WACK-/Tk-Artefakte übersprungen. Der frühere
  `web_companion/` ist seit `05705f9` entfernt; die Profildokumentation macht
  diesen aktuellen Desktop-/Offline-Scope nun ausdrücklich sichtbar.

### Maintainer verification (2026-08-02)
- Der lokale Pytest-Lauf bestand mit 59 Tests und übersprang 4 Tests wegen
  fehlender lokaler Store-/MSIX-/WACK-Artefakte. `unix_preflight.py` fand über
  12 Artefakte keine Befunde; der deprecated Linux-Wrapper über 11 ebenfalls.
- Ruff meldet 18 bestehende Befunde; im MAINTAINER-Lauf wurde kein Code geändert.

### Maintainer verification (2026-08-01)
- Lokaler Pytest-Lauf: 55 Tests bestanden, 8 wegen absichtlich lokaler Store-/WACK-
  Artefaktgrenzen und fehlender Tk-Dateien übersprungen. `unix_preflight.py` fand
  über 12 Artefakte keine Befunde; der deprecated Linux-Wrapper über 11 ebenfalls.

### Geändert / Changed (2026-07-30)
- Discoverability, README-Design & SEO Audit (Pfad B): `llms.txt` Header auf `Last-checked: 2026-07-30` und Testsuite-Status (56 passed, 7 skipped) aktualisiert.
- `README.md` & `README_de.md` Badges und Sichtbarkeits-Timestamps auf 2026-07-30 synchronisiert; bilinguale Badge-Reihe in `README_de.md` zur optischen Nutzerführung ergänzt.

### Geändert / Changed (2026-07-29)
- TASKPLAN #890 / TW-WSP-03: Runtime-Dependency-Checks installieren keine Pakete mehr beim GUI-Start. Der standardbibliotheksbasierte Release-Contract prüft Requirements, Lizenzprovenienz, Store-Claims, Projektprofil und Store-Metadaten reproduzierbar; die öffentliche Store-Version folgt jetzt `pyproject.toml` (`3.1.0.0`).

### Geändert / Changed (2026-07-29)
- `TW-WSP-02`: Maschinenspezifische Einstellungen und rotierende UTF-8-Laufzeitlogs liegen nun
  außerhalb des Quell-Checkouts in den nativen Host-Datenpfaden. Gültige alte
  `settings_store_packager.json`-Dateien werden atomar und ohne Überschreiben bestehender
  Runtime-Einstellungen migriert; Zertifikatspasswörter bleiben ausschließlich im Keyring.

### Behoben / Fixed (2026-07-29)
- Veraltete Verweise auf den entfernten `web_companion/` aus `README.md` und `llms.txt` entfernt; die öffentliche Dokumentation beschreibt nur die vorhandenen Desktop- und SDK-freien Preflight-Workflows.
- Regressionstest ergänzt, damit öffentliche Einstiegsdokumente nicht erneut auf den entfernten lokalen Web-Helfer verweisen.

### Geändert / Changed (2026-07-26)
- CI überspringt absichtlich nicht versionierte WACK-Protokolle und Tkinter-UI-Tests ohne verfügbares Display, statt dadurch die plattformübergreifende Quellprüfung fälschlich fehlschlagen zu lassen.
- Technische Hygiene & Doku-Wartung: `llms.txt` Header auf `Last-checked: 2026-07-26` und Testsuite-Status (33 Tests) aktualisiert.
- `README.md` und `README_de.md` aktualisiert: Shields.io Badges, GFM LLM Integrations-Hinweis (`> [!NOTE]`) & Mermaid Architektur-/Paketierungs-Pipeline Diagramm eingebunden.

### Geändert / Changed (2026-07-25)
- Standardisiertes PEP 621 `pyproject.toml` mit Paket-Metadaten und Pytest-Konfiguration (`pythonpath = ["."]`) angelegt.
- GitHub Actions CI-Workflow (`.github/workflows/ci.yml`) für Python 3.10–3.12 auf Windows & Linux hinzugefügt.
- Testsuite-Resilienz in `tests/test_store_dogfood_readiness.py` und `tests/test_threading_bugs.py` gehärtet (30 passed, 3 skipped).
- README.md und README_de.md aktualisiert (Shields.io Badges, GFM LLM Integrations-Hinweis `> [!NOTE]` hinzugefügt, veraltete web_companion-Referenzen bereinigt).
- `llms.txt` Header auf `Last-checked: 2026-07-25` aktualisiert, veraltete web_companion-Dateireferenzen entfernt, Testsuite-Verifikation (33 Tests) ergänzt.

### Hinzugefügt / Added
- `tests/test_windows_source_smoke.py` und Windows-Matrix-Ziel in `.github/workflows/source-platform-smoke.yml` für Windows-Source-Smoke CI-Parität ergänzt (TASKPLAN #894 / TW-WSP-07).
- `winstorepackager-project-v1.json` als eigenes Self-Dogfooding-Profil ergänzt; es enthält Store-Metadaten, Projektpfade und Listing-Kontext ohne Publisher-DN, SDK-Pfade oder Zertifikatsdaten.
- `tests/test_self_dogfood_profile.py` validiert das eigene Projektprofil gegen `store_package.json`, prüft sensible Felder und führt den SDK-freien Preflight mit dem Profil aus.
- `generate_store_screenshots.py` erzeugt ein kuratiertes Microsoft-Store-Screenshot-Set mit vier 1920x1080-PNGs ohne Publisher-, Zertifikats- oder Privatpfad-Daten.
- `tests/test_store_screenshots.py` prüft Dateinamen, PNG-Format, Abmessungen und Nicht-Leerheit des generierten Store-Screenshot-Sets.
- `unix_preflight.py` ergänzt: SDK-freier Unix-Preflight (für Linux und macOS) prüft Projektstruktur, `store_package.json`, README, Privacy Policy, Store-Listing, Screenshot-/Icon-Artefakte und optional exportierte Projektprofile.
- `tests/test_unix_preflight.py` deckt gültige Unix-Preflights, fehlende Artefakte, Drift zwischen Projektprofil und Store-Metadaten sowie den Abwärtskompatibilitäts-Wrapper ab.
- `llms.txt` als maschinenlesbarer Projektkontext für Crawler, LLMs und Repo-Navigation ergänzt.
- `PORTIERUNGSPLAN.md` ergänzt: Windows Store bleibt Hauptkanal, `web_companion/` bleibt lokaler Hilfsweg für Projektprofile; Android/iOS sind Nicht-Ziele, macOS/Linux bleiben SDK-freier Preflight.
- Projektaufgaben um P0-P3-Portierungsschritte für Dogfooding, Austauschformat `winstorepackager-project-v1.json`, lokalen Helper-Scope und Preflight ergänzt.
- `PROJECT_PROFILE_FORMAT.md` dokumentiert jetzt das gemeinsame Austauschformat `winstorepackager-project-v1.json`.
- Desktop-App kann Projektprofile jetzt sicher importieren und exportieren, ohne Publisher-ID, SDK-Pfade oder Zertifikatsdaten mitzuschreiben.
- `web_companion/` als lokaler Projektprofil-Helfer für Manifest-Vorschau, Icon-Check und JSON-Import/Export ergänzt.
- `web_companion/` hat jetzt eine optionale installierbare Offline-Hülle: `service-worker.js`, `offline.html`, `icon.svg` und `serve_companion.py` ergänzen lokalen Cache, Install-Flow und localhost-Start für denselben lokalen Helper.
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
