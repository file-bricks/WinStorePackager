# TASKPLAN Readback — Task 1431 (RERUN12)

- **Prüfzeit:** 2026-08-12 19:04:15 +02:00 (Europe/Berlin)
- **Task:** `[WinStorePackager] winstorepackager-project-v1 Profile Import/Export Schema verifizieren`
- **Taskplan-Status:** `open` / `blocked_dependency`, `assigned_to=tasksolver-codex`
- **Selektor-Projektpfad:** `C:\_Local_DEV\repos\WinStorePackager`
- **Taskvertrag:** JSON-Write/Read/Serialize-Roundtrip und cross-platform Windows-Drive-Path-Regression sind nachzuweisen; der direkte Desktop↔Web-Pytest bleibt bis zu einem autorisierten Web-Client offen.

## Checkout-, Remote- und Fremdgrenze

- Lokaler `master`-Checkout: `26980aa685f878b0a2e14d5743cc21c4be358436`, **ahead 21 / behind 2** gegenüber `origin/master`.
- Frischer `git ls-remote origin HEAD refs/heads/master`: `e28b2d85c946a7811da2ebe5609253f155b45727` für beide Referenzen; kein `origin/main`-Treffer.
- `git diff --check` ist sauber; keine `LOCK*`-Datei. Die einzige aktuelle Checkout-Abweichung ist das vorbestehende fremde ungetrackte `TASKPLAN_STATUS_2026-08-12_1431-rerun7.md`; es wurde nicht übernommen, geändert, gestaged oder gelöscht.
- Es gab keinen Fetch, Pull, Push, Release-, MSIX-, Store- oder Upload-Schritt.

## Frische lokale Schema- und Preflight-Verifikation

- `winstorepackager-project-v1.json`: JSON-valide, 1354 Bytes, SHA-256 `A849B952818DE5F964979747C2412F181195BB4645F9DA887675AA0CA7C90A76`; `format=winstorepackager-project-v1`, `schema_version=1`, keine Publisher-DN-, SDK-, Zertifikats- oder Passwortwerte.
- Profil-/Preflight-/Source-Smoke-/Release-Contract-Lauf (`test_project_profile.py`, `test_self_dogfood_profile.py`, `test_unix_preflight.py`, `test_windows_source_smoke.py`, `test_store_dogfood_readiness.py`, `test_release_contract.py`): **23 passed, 4 skipped**.
- Die vollständige Sammlung enthält **66 Tests**. Der letzte vollständige `pytest -q -ra`-Lauf bestand mit **61 passed, 5 skipped**; die Skips betreffen fehlende lokale Store-/MSIX-Artefakte, das absichtlich nicht versionierte WACK-Protokoll und die unvollständige Tkinter-Display-Umgebung. Der deterministische Lauf ohne `tests/test_threading_bugs.py` bestand mit **57 passed, 4 skipped**.
- `$env:PYTHONIOENCODING='utf-8'; python -B -X utf8 unix_preflight.py --project-root . --profile-path winstorepackager-project-v1.json --json`: `ok=true`, 0 Fehler, 0 Warnungen, 12 geprüfte Artefakte.
- `$env:PYTHONIOENCODING='utf-8'; python -B -X utf8 -m compileall -q project_profile.py unix_preflight.py tests`: Exit 0.
- Gezielter Ruff-Lauf für `project_profile.py`, `unix_preflight.py` und die relevanten Profil-/Preflight-Tests: **All checks passed**. Ein breiter Ruff-Lauf über alle Tests meldet vier vorbestehende Befunde außerhalb dieses Vertrags (`test_bug_regressions.py`, `test_threading_bugs.py`, `test_wack_and_signing.py`); sie wurden nicht verändert.

## Desktop↔Web-Gate

- `Test-Path web_companion` im kanonischen Checkout: `False`.
- Git-Historie bestätigt den autorisierten Abbau in Commit `05705f9ab665fccf1752d03388d685893ac1f0ad` (`refactor!: remove web companion (no user usecase per 2026-07-23 audit)`).
- Es wurde kein Dummy-Frontend, kein Ersatzclient und kein Wiederherstellungs-Commit angelegt. Damit ist der ausdrücklich verlangte direkte Desktop↔Web-Import-/Export-Pytest aktuell nicht ausführbar; Task 1431 bleibt `open` / `blocked_dependency`.

## OneDrive-Projektion / Steuerdokumente

- Der Spiegel `C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\CODING\REL-PUB_WinStorePackager` wurde mit FileCommander ausschließlich gelesen; `cldflt.sys` ist aktiv, Lock-/Rename-Risiko **hoch**. Kein Writeback, Rename, Sync oder Merge.
- Die OneDrive-Steuertexte sind gegenüber dem lokalen Plan-D-Checkout veraltet: `PROJECT_PROFILE_FORMAT.md` beschreibt noch einen Desktop↔Web-Companion-Workflow und `README.md`/`CHANGELOG-WORKSTATION-LG.md` führen ältere Test- und Companion-Stände. Diese Divergenz ist dokumentiert, nicht durch einen riskanten Schreibvorgang verdeckt.

## Ergebnis

Der lokale Profil-/Schema-Vertrag, der Self-Dogfood-Import/Export-Roundtrip und die Windows-Drive-Portabilität sind frisch verifiziert. Der direkte Desktop↔Web-Nachweis bleibt wegen des fehlenden autorisierten Web-Clients offen. Es erfolgte keine Produkt-, Store-, MSIX-, Release- oder Remote-Mutation; eigener Inhalt dieses Laufs ist nur dieser Readback.
