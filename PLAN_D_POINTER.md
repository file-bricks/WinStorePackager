# Plan-D-Pointer — WinStorePackager

Stand: 2026-07-22

Die lokale Code-Arbeitskopie liegt unter
`<LOCAL_DEV_REPOS>\WinStorePackager` auf `master` mit Remote
`https://github.com/file-bricks/WinStorePackager.git`. Vor der Arbeit waren
Remote, OneDrive-HEAD und Clone-HEAD auf
`94f0ce385faafed610f9b55663976f8bd43a9cde` tree-identisch; die TASKSOLVER-
Änderung liegt lokal in `d1f805d` und ist nicht gepusht.

Build-Caches, PyInstaller-Workfiles, EXE, Start-Smoke und Provenienz liegen
ausschließlich unter `<LOCAL_DEV_ROOT>\codex_build\WinStorePackager`. Die
vorhandenen fremden OneDrive-Git-Änderungen und untracked Assets wurden weder
verschoben, gelöscht noch übernommen. Dieser Pfad führt nur noch Pointer,
Dokumentation und bewusst kuratierte Artefakte.
