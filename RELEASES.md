# RELEASES - WinStorePackager

Stand: 2026-05-01
Aktuelles lokales EXE-Bundle: `v2.3.0`

## Struktur

```text
releases/
├── v2.3.0/
│   ├── WinStorePackager-2.3.0-win64.exe
│   ├── WinStorePackager-2.3.0-source.zip
│   ├── CHANGELOG.txt
│   └── SHA256SUMS.txt
└── windowsstore/
    └── ...
```

## Aktueller Stand

- `dist/WinStorePackager.exe` ist der frische lokale Build aus dem aktuellen Quellstand.
- `releases/v2.3.0/` enthaelt die versionierten GitHub-/Direktdownload-Artefakte.
- `releases/windowsstore/` bleibt getrennt fuer den MSIX-/Store-Workflow.
- Release-Artefakte bleiben lokal ignoriert und werden nicht direkt in Git versioniert.

## Letzte Pflege

- 2026-05-01: README, Privacy-Hinweise und Git-Ignore-Regeln fuer lokale Release-/Staging-Artefakte aktualisiert.
- 2026-04-29: Lokales EXE-Bundle, Source-ZIP und Checksummen aus dem aktuellen Arbeitsstand aktualisiert.
