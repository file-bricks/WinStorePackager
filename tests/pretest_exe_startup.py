"""Pretest-Haertung — WELLE-1-USERTEST U1d (2026-07-23/24).

LUECKENBEFUND: Der bisherige, dokumentierte Pretest ("10 PASS / 0 FAIL")
bestand ausschliesslich aus pytest-Unittests, die WindowsStorePublisher_3.py
als PYTHON-QUELLMODUL importieren (siehe tests/test_bug_regressions.py,
tests/test_threading_bugs.py, tests/test_utils.py: "import
WindowsStorePublisher_3 as _wsp"). Ein Quellimport laeuft im normalen
Dev-Interpreter, in dem keyring/Pillow/pygetwindow direkt installiert sind --
er prueft NIE, ob PyInstaller diese Module tatsaechlich in die Frozen-EXE
gebuendelt hat. Deshalb konnte "ModuleNotFoundError: No module named
'keyring'" beim Start der echten Release-EXE unentdeckt bleiben, obwohl alle
Unittests gruen waren. Kein einziger vorhandener Test hat je die gebaute EXE
tatsaechlich gestartet.

DIESES SKRIPT SCHLIESST GENAU DIESE LUECKE: Es startet die reale
dist\\WinStorePackager.exe (bzw. einen uebergebenen Pfad -- z. B. eine
releases\\...-EXE) als eigenen Windows-Prozess und prueft:

  1. Der Prozess crasht nicht sofort (ueberlebt STABLE_SECONDS).
  2. Die Prozesszahl bleibt stabil bei <= MAX_EXPECTED_PROCESSES (PyInstaller
     --onefile erzeugt normalerweise 2: Bootloader + entpackter Kindprozess).
     Ein WEITER WACHSENDER Prozesszaehler ist das Fork-Bomben-Signaturmuster
     aus AUFGABEN.txt U1f (real: 491 Prozesse durch einen
     sys.executable-Aufruf, der die EXE selbst statt pip re-startete).
  3. Der Prozess reagiert (Responding=True), kein Absturz auf ein
     "Nicht mehr reagiert"-Fenster.

Kein pytest-Unittest: startet einen echten Prozess mit GUI-Fenster, daher
NICHT Teil von `pytest tests/` (dort liefe es in jeder CI/jedem Nicht-Windows-
Runner ins Leere oder wuerde ein reales Fenster oeffnen). Aufruf manuell oder
aus dem Pretest-/Store-Welle-Ablauf heraus:

    PYTHONIOENCODING=utf-8 python tests\\pretest_exe_startup.py [pfad\\zur.exe]

Exit-Code 0 = PASS, 1 = FAIL (Fork-Bomben-Verdacht oder Crash) -- in beiden
Faellen werden alle gestarteten Prozesse am Ende sauber beendet.
"""
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_EXE = REPO_ROOT / "dist" / "WinStorePackager.exe"

STABLE_SECONDS = 8          # Beobachtungsfenster nach dem Start.
POLL_INTERVAL = 2           # Sekunden zwischen Prozesszahl-Messungen.
MAX_EXPECTED_PROCESSES = 3  # Bootloader + Kindprozess + Toleranz; alles darueber = Verdacht.


def _list_matching_pids(exe_name):
    """PIDs aller laufenden Prozesse mit diesem Image-Namen (PowerShell/Get-Process)."""
    ps_cmd = (
        f"(Get-Process -Name '{exe_name}' -ErrorAction SilentlyContinue) "
        "| Select-Object -ExpandProperty Id"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
        capture_output=True, text=True, timeout=30,
    )
    pids = [int(line.strip()) for line in result.stdout.splitlines() if line.strip().isdigit()]
    return pids


def _kill_all(exe_name):
    subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command",
         f"Get-Process -Name '{exe_name}' -ErrorAction SilentlyContinue | Stop-Process -Force"],
        capture_output=True, text=True, timeout=30,
    )


def run_pretest(exe_path: Path) -> bool:
    if not exe_path.exists():
        print(f"❌ FAIL: EXE nicht gefunden: {exe_path}")
        return False

    exe_name = exe_path.stem  # z.B. "WinStorePackager"

    pre_existing = _list_matching_pids(exe_name)
    if pre_existing:
        print(f"⚠️  WARNUNG: Bereits laufende '{exe_name}'-Prozesse vor dem Test: {pre_existing}. "
              "Breche ab, um keinen falschen Fork-Bomben-Alarm auszuloesen.")
        return False

    print(f"--- Starte {exe_path} (EIN kontrollierter Startversuch) ---")
    subprocess.Popen([str(exe_path)])

    ok = True
    max_seen = 0
    elapsed = 0
    try:
        while elapsed < STABLE_SECONDS:
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            pids = _list_matching_pids(exe_name)
            max_seen = max(max_seen, len(pids))
            print(f"  t={elapsed}s: {len(pids)} Prozess(e) -> PIDs {pids}")
            if len(pids) > MAX_EXPECTED_PROCESSES:
                print(f"❌ FAIL: FORK-BOMBEN-VERDACHT — {len(pids)} Prozesse "
                      f"(Grenzwert {MAX_EXPECTED_PROCESSES}). Sofortiger Abbruch.")
                ok = False
                break

        if ok:
            final_pids = _list_matching_pids(exe_name)
            if not final_pids:
                print("❌ FAIL: Prozess ist innerhalb des Beobachtungsfensters verschwunden (Absturz?).")
                ok = False
            else:
                print(f"✅ PASS: Prozesszahl stabil (max. {max_seen} <= {MAX_EXPECTED_PROCESSES}), "
                      f"Prozess laeuft nach {STABLE_SECONDS}s weiter.")
    finally:
        print("--- Räume auf: beende alle gestarteten Prozesse ---")
        _kill_all(exe_name)
        time.sleep(1)
        remaining = _list_matching_pids(exe_name)
        if remaining:
            print(f"⚠️  WARNUNG: Nach Stop-Process verbleiben PIDs {remaining} — manuell prüfen.")
        else:
            print("--- 0 Prozesse verbleiben. ---")

    return ok


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_EXE
    success = run_pretest(target)
    sys.exit(0 if success else 1)
