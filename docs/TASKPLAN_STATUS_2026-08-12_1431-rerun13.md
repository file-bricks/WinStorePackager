# TASKPLAN-Readback — WinStorePackager profile exchange (Task 1431, RERUN13)

**Prüfzeit:** 2026-08-12 19:56:16 +02:00  
**Rolle:** `tasksolver-codex`  
**Selektor-Bündel:** ausschließlich Task `1431`  
**Plan-D-Checkout:** `C:\_Local_DEV\repos\WinStorePackager`

## Task-, Checkout- und Fremdgrenze

- Task 1431 bleibt in der TASKPLAN-Datenbank `open`, `assigned_to=tasksolver-codex` und `delegation_status=blocked_dependency`. Der Taskvertrag verlangt JSON-Write/Read/Serialize-Roundtrip, Windows-Laufwerkspfad-Portabilität und ausdrücklich den Desktop↔Web-Import/Export-Nachweis.
- Der Checkout ist auf `master`, `HEAD=9fea5c2733b8644be632382f49e6ed4c1e730269`. Die lokale `origin/master`-Ref ist `4d701c037de7366f954c4e49d9629557e2606b05` (`master...origin/master [ahead 22, behind 2]`); der Live-Remote meldet separat `e28b2d85c946a7811da2ebe5609253f155b45727` für `refs/heads/master`. Es wurde weder gefetcht noch gepullt.
- Der Checkout ist tracked-sauber; das vorbestehende untracked `TASKPLAN_STATUS_2026-08-12_1431-rerun7.md` blieb unangetastet. `git diff --check` ist sauber, und es wurden keine `LOCK*`-, `index.lock`- oder `REPO.pointer`-Dateien gefunden.
- Es gab keinen Produkt-, Store-, MSIX-, WACK-, Release-, Upload- oder Remote-Writeback. Dieses Readback ist der einzige eigene Writeback dieses Bündels.

## Frische lokale Schema- und Preflight-Verifikation

- `winstorepackager-project-v1.json` ist JSON-valide, 1354 Bytes groß und hat SHA-256 `A849B952818DE5F964979747C2412F181195BB4645F9DA887675AA0CA7C90A76`.
- Der Vertrag ist `format=winstorepackager-project-v1`, `schema_version=1` mit den Bereichen `metadata`, `paths`, `store`, `documents` und `settings`. Das Profil enthält keine Publisher-DN-, SDK-, Zertifikats-, Passwort- oder Keyring-Werte.
- Profil-/Preflight-/Source-Smoke-/Release-Contract-Fokus (`test_project_profile.py`, `test_self_dogfood_profile.py`, `test_unix_preflight.py`, `test_windows_source_smoke.py`, `test_release_contract.py`): **22 passed, 1 skipped**; der Skip ist das absichtlich nicht versionierte lokale WACK-Protokoll.
- Vollständige Suite: **60 passed, 6 skipped**. Die Skips betreffen optionale lokale Store-/MSIX-/WACK-Artefakte und die lokale Tk-Display-Umgebung.
- `python -B -X utf8 unix_preflight.py --project-root . --profile-path winstorepackager-project-v1.json --json`: `ok=true`, 0 Fehler, 0 Warnungen, 12 geprüfte Artefakte.
- `python -B -X utf8 -m compileall -q project_profile.py unix_preflight.py linux_preflight.py release_contract.py WindowsStorePublisher_3.py tests`: Exit 0.
- Der fokussierte Ruff-Lauf für Profil-/Preflight-/Release-Dateien und die zugehörigen Tests ist **All checks passed**. Ein breiter Ruff-Lauf meldet fünf vorbestehende, außerhalb dieses Vertrags liegende Befunde in `linux_preflight.py`, `tests/test_bug_regressions.py`, `tests/test_threading_bugs.py` und `tests/test_wack_and_signing.py`; diese wurden nicht verändert.

## Roundtrip und Pfadsemantik

- Die vorhandenen Tests belegen `write -> read -> serialize`, relative Projektpfade, fremde Windows-Laufwerke und Windows-Projektwurzeln auf Nicht-Windows-Hosts.
- Der Self-Dogfood-Import ist inhaltlich konsistent und secret-frei. Beim direkten Vergleich von `serialize_project_profile(read_project_profile(...))` mit der kuratierten JSON unterscheidet sich nur die Darstellung von `project_root`: exportierte Zustände werden kanonisch absolut (`C:/_Local_DEV/repos/WinStorePackager`) statt der handgeschriebenen Kurzform `.`; die Profilfelder und relativen Pfade bleiben gleich.

## Desktop↔Web-Gate

- `web_companion/` ist im aktuellen Checkout nicht vorhanden. Die Git-Historie bestätigt den autorisierten Abbau in Commit `05705f9ab665fccf1752d03388d685893ac1f0ad` (`refactor!: remove web companion (no user usecase per 2026-07-23 audit)`).
- Es wurde kein Dummy-Frontend, kein Ersatzclient und kein Wiederherstellungs-Commit angelegt. Ein echter Desktop↔Web-Import-/Export-Pytest ist damit nicht ausführbar; Task 1431 bleibt wegen dieser fehlenden autorisierten Integrationskante `open` / `blocked_dependency`.

## OneDrive-Projektion und Disposition

- Die Projektion `C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\CODING\REL-PUB_WinStorePackager` wurde ausschließlich mit FileCommander gelesen. `cldflt.sys` ist aktiv, das Cloud-/Rename-Risiko hoch; dort gab es keinen Writeback, Rename, Sync oder Merge.
- Die Projektion enthält eine ältere Profilfassung (`version=2.3.0.0`) gegenüber dem lokalen Checkout (`version=3.1.0.0`) und ist laut `WinStorePackager.repo.md` eine nicht-lebende Deploykopie. Diese Drift bleibt unangetastet und wird nicht als lokaler Schema-Nachweis ausgegeben.

Der lokale Desktop-/Offline-Profilvertrag ist grün verifiziert; der direkte Desktop↔Web-Nachweis bleibt wegen des entfernten Web-Clients offen. Task 1431 bleibt **open / `blocked_dependency`**. Danach wird ausschließlich der exakte Projektpfad geskippt; das persistierte TASKSOLVER-Goal bleibt aktiv.
