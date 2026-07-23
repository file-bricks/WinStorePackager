"""Regressionstests — WELLE-1-USERTEST U1 (2026-07-23/24), Startcrash + Fork-Bombe.

Ursachenkette (siehe AUFGABEN.txt, WELLE-1-USERTEST 2026-07-23):
  1) keyring war nicht in den PyInstaller-Build gebuendelt (leeres
     hiddenimports=[] in WinStorePackager.spec) -> in der Frozen-EXE
     "ModuleNotFoundError: No module named 'keyring'".
  2) install_and_import() versuchte daraufhin, das fehlende Modul zur
     Laufzeit per "sys.executable -m pip install ..." nachzuinstallieren.
     In einer Frozen-EXE zeigt sys.executable auf die EXE selbst -> der
     Aufruf startet die App erneut statt pip (Fork-Bombe, real 491
     Prozesse). Der abschliessende input()-Aufruf crashte zusaetzlich mit
     "lost sys.stdin", da eine --windowed-EXE keine Konsole/kein stdin hat.

Diese Tests stellen sicher, dass beide Ursachen behoben bleiben:
  - install_and_import() darf in einer Frozen-EXE (sys.frozen=True) NIEMALS
    subprocess/pip aufrufen und NIEMALS input() nutzen.
  - Die Spec-Datei buendelt keyring (inkl. Windows-Backend/win32ctypes)
    explizit ueber hiddenimports.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))
import WindowsStorePublisher_3 as _wsp

REPO_ROOT = Path(__file__).parent.parent


class TestFrozenGuardNoSubprocessFallback(unittest.TestCase):
    """Kern-Regression: keine Laufzeit-pip-Nachinstallation in Frozen-Builds."""

    def _run_install_and_import_frozen(self, package_name, import_name):
        """Ruft install_and_import() mit sys.frozen=True und garantiert
        fehlendem Modul auf; liefert (check_call_mock, exit_mock)."""
        with mock.patch.object(sys, "frozen", True, create=True), \
             mock.patch.object(_wsp.subprocess, "check_call") as mock_check_call, \
             mock.patch.object(_wsp.sys, "exit", side_effect=SystemExit(1)) as mock_exit, \
             mock.patch("builtins.input") as mock_input, \
             mock.patch("tkinter.Tk") as mock_tk, \
             mock.patch("tkinter.messagebox.showerror") as mock_showerror:
            mock_tk.return_value = mock.MagicMock()
            with self.assertRaises(SystemExit):
                _wsp.install_and_import(package_name, import_name)
        return mock_check_call, mock_exit, mock_input, mock_showerror

    def test_frozen_missing_module_never_calls_subprocess(self):
        """FORK-BOMBEN-REGRESSION: subprocess.check_call darf bei sys.frozen=True
        niemals aufgerufen werden, auch nicht bei fehlendem Modul."""
        mock_check_call, mock_exit, mock_input, _ = self._run_install_and_import_frozen(
            "definitely-not-a-real-package-xyz", "definitely_not_a_real_module_xyz"
        )
        mock_check_call.assert_not_called()

    def test_frozen_missing_module_never_calls_input(self):
        """'lost sys.stdin'-REGRESSION: input() darf in einer Frozen-EXE
        nicht aufgerufen werden (kein stdin in --windowed-Build)."""
        _, _, mock_input, _ = self._run_install_and_import_frozen(
            "definitely-not-a-real-package-xyz", "definitely_not_a_real_module_xyz"
        )
        mock_input.assert_not_called()

    def test_frozen_missing_module_exits_cleanly(self):
        """Bei fehlendem Modul in einer Frozen-EXE muss der Prozess sauber
        beendet werden (sys.exit), statt haengen zu bleiben oder zu respawnen."""
        _, mock_exit, _, _ = self._run_install_and_import_frozen(
            "definitely-not-a-real-package-xyz", "definitely_not_a_real_module_xyz"
        )
        mock_exit.assert_called_with(1)

    def test_non_frozen_still_uses_pip_fallback(self):
        """Gegenprobe: Der Quellstart (kein sys.frozen) darf weiterhin den
        bestehenden pip-Fallback nutzen -- der Fix betrifft NUR Frozen-Builds."""
        self.assertFalse(getattr(sys, "frozen", False),
                          "Testumgebung darf nicht bereits sys.frozen gesetzt haben")
        with mock.patch.object(_wsp.subprocess, "check_call") as mock_check_call, \
             mock.patch.object(_wsp.importlib, "import_module") as mock_import:
            # 1. Aufruf wirft ImportError (Modul fehlt), 2. Aufruf (nach "Installation") klappt.
            mock_import.side_effect = [ImportError(), mock.DEFAULT]
            _wsp.install_and_import("some-package", "some_module")
        mock_check_call.assert_called_once()


class TestHasKeyringReflectsRealImport(unittest.TestCase):
    """HAS_KEYRING war hartkodiert True ('Jetzt garantiert') -- unabhaengig
    davon, ob der keyring-Import tatsaechlich geklappt hat."""

    def test_has_keyring_matches_actual_keyring_import(self):
        self.assertEqual(_wsp.HAS_KEYRING, _wsp.keyring is not None,
                          "HAS_KEYRING muss den echten Import-Status widerspiegeln, "
                          "nicht hartkodiert True sein")

    def test_source_has_keyring_not_hardcoded_true(self):
        src = (REPO_ROOT / "WindowsStorePublisher_3.py").read_text(encoding="utf-8")
        self.assertNotIn("HAS_KEYRING = True", src,
                          "HAS_KEYRING wieder hartkodiert -- Regression von BUG U1")


class TestFatalMissingModuleFrozenExists(unittest.TestCase):
    """Der saubere Fehlerdialog-Pfad fuer Frozen-Builds muss vorhanden und
    ohne subprocess/input aufrufbar sein."""

    def test_fatal_missing_module_frozen_exists(self):
        self.assertTrue(hasattr(_wsp, "_fatal_missing_module_frozen"),
                         "_fatal_missing_module_frozen() fehlt")

    def test_fatal_missing_module_frozen_exits_without_subprocess_or_input(self):
        with mock.patch.object(_wsp.subprocess, "check_call") as mock_check_call, \
             mock.patch("builtins.input") as mock_input, \
             mock.patch.object(_wsp.sys, "exit", side_effect=SystemExit(1)) as mock_exit, \
             mock.patch("tkinter.Tk") as mock_tk, \
             mock.patch("tkinter.messagebox.showerror") as mock_showerror:
            mock_tk.return_value = mock.MagicMock()
            with self.assertRaises(SystemExit):
                _wsp._fatal_missing_module_frozen("keyring", "keyring")
        mock_check_call.assert_not_called()
        mock_input.assert_not_called()
        mock_exit.assert_called_with(1)


class TestSpecFileBundlesKeyring(unittest.TestCase):
    """BUG U1a: WinStorePackager.spec hatte hiddenimports=[] -- keyring (inkl.
    Windows-Backend) wurde dadurch nicht in die Frozen-EXE gebuendelt."""

    def setUp(self):
        self.spec_src = (REPO_ROOT / "WinStorePackager.spec").read_text(encoding="utf-8")

    def test_spec_collects_keyring_submodules(self):
        self.assertIn("collect_submodules('keyring')", self.spec_src,
                      "Spec-Datei buendelt keyring-Submodule nicht mehr — BUG U1a Regression")

    def test_spec_collects_win32ctypes_submodules(self):
        self.assertIn("collect_submodules('win32ctypes')", self.spec_src,
                      "Spec-Datei buendelt win32ctypes (keyring Windows-Backend) nicht — BUG U1a Regression")

    def test_spec_hiddenimports_not_empty(self):
        self.assertNotIn("hiddenimports=[],", self.spec_src,
                          "hiddenimports wieder leer — BUG U1a Regression")


if __name__ == "__main__":
    unittest.main()
