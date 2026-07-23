# RELEASES - WinStorePackager

Stand: 2026-07-24
Aktuelles lokales EXE-Bundle: `v2.3.1`

## Struktur

```text
releases/
├── v2.3.0/
│   ├── WinStorePackager-2.3.0-win64.exe
│   ├── WinStorePackager-2.3.0-source.zip
│   ├── CHANGELOG.txt
│   └── SHA256SUMS.txt
├── v2.3.1/
│   ├── WinStorePackager-2.3.1-win64.exe
│   ├── CHANGELOG.txt
│   └── SHA256SUMS.txt
└── windowsstore/
    └── ...
```

## Aktueller Stand

- `dist/WinStorePackager.exe` ist der frische lokale Build aus dem aktuellen Quellstand.
- `releases/v2.3.1/` enthält den Fix für den Frozen-EXE-Startcrash (WELLE-1-USERTEST U1 CRITICAL, siehe CHANGELOG.md) und die sichtbare Sprachumschaltung (U2).
- `releases/v2.3.0/` bleibt als vorherige versionierte GitHub-/Direktdownload-Artefakte erhalten.
- `releases/windowsstore/` bleibt getrennt für den MSIX-/Store-Workflow.
- Release-Artefakte bleiben lokal ignoriert und werden nicht direkt in Git versioniert.

## Letzte Pflege

- 2026-07-24: `v2.3.1` gebaut — behebt den kritischen Startcrash/Fork-Bombe der v2.3.0-Release-EXE (fehlende keyring-hiddenimports) und ergänzt eine sichtbare Sprachumschaltung Deutsch/Englisch.
- 2026-05-17: Repo-Hygiene geprüft; `.gitattributes` ergänzt und Ignore-Regeln für Store-/Signierartefakte erweitert.
- 2026-05-01: README, Privacy-Hinweise und Git-Ignore-Regeln für lokale Release-/Staging-Artefakte aktualisiert.
- 2026-04-29: Lokales EXE-Bundle, Source-ZIP und Checksummen aus dem aktuellen Arbeitsstand aktualisiert.
