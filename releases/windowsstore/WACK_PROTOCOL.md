# WinStorePackager - Store-Testprotokoll

Stand: 2026-11-07 (Tier-2 6-Sprachen Store-Readiness)

## Artefaktstatus

| Prüffeld | Status | Nachweis |
|---|---|---|
| EXE | buildbereit | `dist/WinStorePackager.exe` |
| MSIX | buildbereit | `releases/WinStorePackager.msix` |
| Store-Konfiguration | vorhanden und JSON-valide | `store_package.json` |
| Self-Dogfooding-Profil | vorhanden und preflight-geprüft | `winstorepackager-project-v1.json` |
| Store-Listing | vorhanden in 6 Sprachen | `STORE_LISTING.md`, `releases/windowsstore/store_listing_*.md` |
| Datenschutz-URL | erreichbar | `https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md` |
| Support-URL | erreichbar | `https://github.com/file-bricks/WinStorePackager/issues` |
| Store-Icons | vorhanden | 44x44, 150x150, 310x310, 310x150 in `store_assets/` |
| Store-Screenshot-Set | vorhanden | `releases/windowsstore/screenshots/01-main-window.png` bis `04-msix-wack-workflow.png`, je 1920x1080 |

## Pre-Submission-Test

SDK-/Adminfreie Readiness, ausgeführt vom Projektroot:

```powershell
python -m pytest -q tests\test_self_dogfood_profile.py tests\test_store_dogfood_readiness.py
```

Ergebnis:

- Self-Dogfooding-Profil ist valide und enthält keine lokalen Secrets.
- Profil, `store_package.json` und `store_settings.json` bleiben bei App-Name, Version, Privacy-URL und Support-URL synchron.
- Store-Listing in allen 6 Sprachen (DE, EN, ES, ZH, JA, RU) enthält App-Name, Privacy-/Support-URLs, kurze Beschreibungen <= 100 Zeichen und keine TODO/FIXME-Marker.
- Store-Screenshot-Set ist vollständig und alle 4 PNGs sind 1920x1080.
- `BUILD.md` und dieses Protokoll enthalten keine alten hardcodierten Pfade (`<PROJECT_ROOT>` / `<SOFTWARE_ROOT>`).

## WACK-Status

Der echte WACK-Paketlauf gegen `releases/WinStorePackager.msix` ist vorbereitet und kann als erhöhter Windows-Prozess ausgeführt werden:

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File "<SOFTWARE_ROOT>\_STORE\msstore_wack.ps1" -MsixPath "<PROJECT_ROOT>\releases\WinStorePackager.msix"'
```

## Lokaler Worker- und Ergebnisvertrag

Der ausführbare WACK-Worker liegt im Plan-D-Clone `C:\_Local_DEV\repos\WinStorePackager`. Er führt `appcert reset` und danach `appcert test` im Hintergrund aus, wartet auf beide Prozesse und unterscheidet `passed`, `failed`, `timed_out`, `cancelled`, `tool_missing` und `start_failed`.
