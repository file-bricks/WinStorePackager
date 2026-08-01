# Plan-D-Pointer — WinStorePackager

Stand: 2026-07-29

Die kanonische Code-Arbeitskopie liegt unter
`C:\_Local_DEV\repos\WinStorePackager` auf `master` mit Remote
`https://github.com/file-bricks/WinStorePackager.git`.

GitHub und der lokale Plan-D-Klon stehen auf
`7e1678cd33a573c8dcfddb37b02a85013750b685`.
Nach dem Abgleich bis `b797f05` führte `51a25e3` maschinenspezifische
Einstellungen, rotierende Runtime-Logs und die Credential-Metadaten aus dem
Checkout in native Host-Datenpfade. Zertifikatspasswörter bleiben im
Betriebssystem-Keyring; Legacy-Einstellungen werden atomar und ohne
Überschreiben vorhandener Runtime-Daten migriert.

`7e1678c` ergänzt den reproduzierbaren Dependency-, Lizenz- und Store-Metadatenvertrag.
Die Rückspiegelung der betroffenen Quell-/Testdateien wurde fail-closed gestoppt:
`CHANGELOG.md`, `WindowsStorePublisher_3.py`, `store_package.json`,
`winstorepackager-project-v1.json` und `tests/test_bugsweep_resweep_20260622.py`
wichen schon vor dem Deploy vom Hash des bestätigten Baselines-Commits `51a25e3` ab.
Diese fremden OneDrive-Diffs sowie das lebende `.git`-Worktree, sechs geänderte
Asset-Dateien und host-suffigierte Konfliktkopien bleiben unangetastet. Sie sind kein
kanonischer Quellstand und nicht Teil dieses Deployments; erst fachlich nachzertifizieren
und bewusst reconciliieren. Details: `.SYNC/workstation/GITHUB_ONEDRIVE_SYNC_WinStorePackager_2026-07-29.md`.

Build-Caches, PyInstaller-Workfiles, EXE, Start-Smoke und Provenienz liegen
ausschließlich unter `C:\_Local_DEV\codex_build\WinStorePackager`.
