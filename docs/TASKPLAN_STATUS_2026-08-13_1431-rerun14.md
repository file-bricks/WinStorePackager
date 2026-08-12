# TASKPLAN-Readback — WinStorePackager profile exchange (Task 1431, RERUN14)

**Prüfzeit:** 2026-08-13 00:36:40 +02:00  
**Rolle:** `tasksolver-codex`  
**Selektor-Bündel:** ausschließlich Task `1431`  
**Plan-D-Checkout:** `C:\_Local_DEV\repos\WinStorePackager`

## Task-, Checkout- und Fremdgrenze

- Task `1431` bleibt in der TASKPLAN-Datenbank `open`, `assigned_to=tasksolver-codex` und `delegation_status=blocked_dependency`. Der Vertrag verlangt JSON-Write/Read/Serialize-Roundtrip, Windows-Laufwerkspfad-Portabilität sowie ausdrücklich einen Desktop↔Web-Import-/Export-Nachweis.
- Der Checkout ist `master`, `HEAD=0734d71cbd3c5254cc901da740e11db41e86ce09`; die lokale `origin/master`-Referenz ist `4d701c037de7366f954c4e49d9629557e2606b05`, der frische Remote-Readback meldet `e28b2d85c946a7811da2ebe5609253f155b45727`. Der Checkout ist 23 Commits voraus und 2 Commits hinter der lokalen Remote-Referenz. Es wurde weder gefetcht noch gepullt.
- Der Code-Arbeitsbaum ist sauber; das vorbestehende untracked `TASKPLAN_STATUS_2026-08-12_1431-rerun7.md` blieb unangetastet. `git diff --check` ist sauber. Es wurden keine `LOCK*`-, `index.lock`- oder `REPO.pointer`-Dateien gefunden.
- Es erfolgte kein Produkt-, Store-, MSIX-, WACK-, Release-, Upload- oder Remote-Writeback. Der lokale Klon liegt außerhalb OneDrive; `cldflt.sys` ist aktiv, Lock-Risiko laut FileCommander mittel. Die OneDrive-Projektion wurde nicht beschrieben.

## Frische Profil- und Preflight-Verifikation

- `winstorepackager-project-v1.json` ist JSON-valide, 1354 Bytes groß und hat SHA-256 `A849B952818DE5F964979747C2412F181195BB4645F9DA887675AA0CA7C90A76`.
- Der Vertrag ist `format=winstorepackager-project-v1`, `schema_version=1` mit den Bereichen `metadata`, `paths`, `store`, `documents` und `settings`. Das Profil enthält keine Publisher-DN-, SDK-, Zertifikats-, Passwort- oder Keyring-Werte.
- Profil-/Preflight-/Source-Smoke-/Release-Contract-Fokus (`test_project_profile.py`, `test_self_dogfood_profile.py`, `test_unix_preflight.py`, `test_windows_source_smoke.py`, `test_release_contract.py`): **22 passed, 1 skipped**; der Skip betrifft das absichtlich nicht versionierte lokale WACK-Protokoll.
- Gesamtsuite `python -B -X utf8 -m pytest tests -q -p no:cacheprovider`: **62 passed, 4 skipped**.
- `python -B -X utf8 unix_preflight.py --project-root . --profile-path winstorepackager-project-v1.json --json`: `ok=true`, 0 Fehler, 0 Warnungen, 12 geprüfte Artefakte.
- `python -B -X utf8 -m compileall -q project_profile.py unix_preflight.py linux_preflight.py release_contract.py WindowsStorePublisher_3.py tests`: Exit 0.
- Fokussierter Ruff-Lauf für Profil-/Preflight-/Release-Dateien und zugehörige Tests: **All checks passed**.

## Roundtrip- und Pfadvertrag

- Die aktuellen Tests belegen `write -> read -> serialize`, relative Projektpfade, fremde Windows-Laufwerke und Windows-Projektwurzeln auf Nicht-Windows-Hosts.
- Das Self-Dogfood-Profil wird importiert, gegen `store_package.json` abgeglichen und vom SDK-freien Preflight akzeptiert. Sensible lokale Werte bleiben außerhalb des exportierten JSON.
- `WindowsStorePublisher_3.py` bindet `write_project_profile` an den Desktop-Export und `read_project_profile` an den Desktop-Import; der Quell-Smoke importiert das Modul ohne Seiteneffekte.

## Desktop↔Web-Gate

- `web_companion/` ist im aktuellen Checkout nicht vorhanden (`Test-Path=False`).
- Die Git-Historie bestätigt den autorisierten Abbau in Commit `05705f9ab665fccf1752d03388d685893ac1f0ad`: `refactor!: remove web companion (no user usecase per 2026-07-23 audit)`; dabei wurden Frontend, Manifest, Service Worker und PWA-Tests entfernt.
- Es wurde kein Dummy-Frontend, kein Ersatzclient und kein Wiederherstellungs-Commit angelegt. Ein echter Desktop↔Web-Import-/Export-Pytest ist damit nicht ausführbar.

## Ergebnis und Disposition

Der lokale Desktop-/Offline-Profilvertrag ist empirisch grün verifiziert. Der ausdrücklich geforderte Desktop↔Web-Nachweis bleibt wegen der autorisiert entfernten Integrationskante offen. Task `1431` bleibt daher **open / `blocked_dependency`**. Dieser Readback ist die einzige eigene Änderung dieses Bündels; fremde Dateien wurden nicht übernommen. Danach wird ausschließlich der exakte Projektpfad geskippt und das persistierte TASKSOLVER-Goal bleibt aktiv.
