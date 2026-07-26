"""
Regressionstests fuer Threading-Bugs in WindowsStorePublisher_3.py:

Bug #1: run_screenshots() rief messagebox.showinfo/showerror direkt aus
        dem Background-Thread auf (Tkinter nicht thread-safe).
Bug #2: run_wack_test() rief subprocess.run([appcert, "reset"]) im
        Hauptthread auf -- GUI blockiert fuer bis zu 30 s.
Bug #3: run_screenshots() rief im Fehlerfall proc.terminate() ohne
        anschliessendes proc.wait() auf -- Zombie-Prozess-Risiko.
Bug #4: except Exception as e in Hintergrundthreads verwendete e direkt
        in Lambdas -- Python 3 loescht e am Ende des except-Blocks
        (NameError wenn Lambda spaeter ausgefuehrt wird).
"""
import os
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

tcl_dir = os.path.join(sys.prefix, 'tcl', 'tcl8.6')
if os.path.exists(tcl_dir):
    os.environ.setdefault('TCL_LIBRARY', tcl_dir)
    os.environ.setdefault('TK_LIBRARY', os.path.join(sys.prefix, 'tcl', 'tk8.6'))

import tkinter as tk
import WindowsStorePublisher_3 as _wsp

# Shared Tkinter root -- one per test module to avoid TclError on reinit.
_tk_root: tk.Tk | None = None


def _get_root() -> tk.Tk:
    global _tk_root
    if _tk_root is None:
        _tk_root = tk.Tk()
        _tk_root.withdraw()
    return _tk_root


def _minimal_app() -> "_wsp.StorePackagerApp":
    """Erstellt StorePackagerApp ohne vollen GUI-Build (kein load_settings/build_gui)."""
    _wsp.Image = MagicMock()
    _wsp.ImageGrab = MagicMock()
    _wsp.gw = MagicMock()
    _wsp.keyring = MagicMock()
    _wsp.keyring.get_password.return_value = None

    app = _wsp.StorePackagerApp.__new__(_wsp.StorePackagerApp)
    tk.Tk.__init__(app)
    app.withdraw()

    app.app_name = tk.StringVar(value="TestApp")
    app.publisher = tk.StringVar(value="CN=Test")
    app.publisher_display = tk.StringVar(value="Test")
    app.identity_name = tk.StringVar(value="Test.TestApp")
    app.version = tk.StringVar(value="1.0.0.0")
    app.script_path = tk.StringVar()
    app.icon_path = tk.StringVar()
    app.source_path = tk.StringVar()
    app.installer_path = tk.StringVar()
    app.output_dir = tk.StringVar(value=str(Path(__file__).parent))
    app.exe_name = tk.StringVar(value="TestApp.exe")
    app.makeappx_path = tk.StringVar()
    app.signtool_path = tk.StringVar()
    app.appcert_path = tk.StringVar(value="fake_appcert.exe")
    app.pfx_path = tk.StringVar()
    app.pfx_password = tk.StringVar()
    app.timestamp_url = tk.StringVar(value="http://timestamp.digicert.com")
    app.msix_name = tk.StringVar(value="TestApp.msix")
    app.python_path = tk.StringVar()
    app.license_files = []
    app.license_text_entries = []
    app.enable_i18n = tk.BooleanVar(value=False)
    app.capabilities = tk.StringVar(value="internetClient")
    app.privacy_url = tk.StringVar()
    app.support_url = tk.StringVar()
    app.category = tk.StringVar(value="Productivity")
    app.age_rating = tk.StringVar(value="3+")
    app.changelog_box = None
    app.readme_box = None
    app.license_box = None
    app.desc_box = None

    return app


class TestWACKTestNonBlocking(unittest.TestCase):
    """Bug #2: subprocess.run([appcert, 'reset']) muss im Hintergrundthread laufen."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.app = _minimal_app()
        except Exception as err:
            raise unittest.SkipTest(f"Tkinter GUI display unavailable: {err}")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def test_run_wack_runs_subprocess_in_background_thread(self):
        reset_thread_ids: list[int] = []
        main_id = threading.main_thread().ident
        done = threading.Event()

        def fake_run(cmd, **kwargs):
            reset_thread_ids.append(threading.current_thread().ident)
            done.set()
            return MagicMock(returncode=0)

        self.app.after = lambda delay, func, *args: None

        with patch("subprocess.run", fake_run), \
             patch("subprocess.Popen"), \
             patch("os.path.exists", return_value=True):
            self.app.run_wack_test()
            done.wait(timeout=3.0)

        self.assertTrue(reset_thread_ids, "subprocess.run wurde nicht aufgerufen")
        self.assertNotEqual(
            reset_thread_ids[0], main_id,
            "subprocess.run lief im Hauptthread -- Bug #2 nicht behoben",
        )


class TestScreenshotsThreadSafety(unittest.TestCase):
    """Bug #1 + Bug #3: run_screenshots() Thread-Sicherheit und proc.wait()."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.app = _minimal_app()
        except Exception as err:
            raise unittest.SkipTest(f"Tkinter GUI display unavailable: {err}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "app"):
            try:
                cls.app.destroy()
            except Exception:
                pass

    def _reset_after(self):
        """Ersetzt self.after mit Capture-Funktion; gibt done-Event zurueck."""
        done = threading.Event()
        captured: list = []

        def capture_after(delay, func, *args):
            captured.append(func)
            done.set()

        self.app.after = capture_after
        return done, captured

    def test_screenshots_showinfo_dispatched_via_after(self):
        """Bug #1: Erfolgsfall nutzt self.after statt direktem messagebox.showinfo."""
        done, captured = self._reset_after()

        fake_proc = MagicMock()
        fake_img = MagicMock()
        fake_img.resize.return_value = MagicMock()
        _wsp.ImageGrab.grab.return_value = fake_img

        with patch("subprocess.Popen", return_value=fake_proc), \
             patch("time.sleep"), \
             patch("os.makedirs"), \
             patch("os.path.exists", return_value=True):
            self.app.run_screenshots()
            done.wait(timeout=5.0)

        self.assertTrue(
            captured,
            "self.after nie aufgerufen -- messagebox.showinfo direkt aus Thread (Bug #1)",
        )

    def test_screenshots_showerror_dispatched_via_after_on_exception(self):
        """Bug #1: Fehlerfall nutzt self.after statt direktem messagebox.showerror."""
        done, captured = self._reset_after()

        fake_proc = MagicMock()

        with patch("subprocess.Popen", return_value=fake_proc), \
             patch("time.sleep", side_effect=RuntimeError("test-exception")), \
             patch("os.path.exists", return_value=True):
            self.app.run_screenshots()
            done.wait(timeout=3.0)

        self.assertTrue(
            captured,
            "self.after nie aufgerufen im Fehlerfall -- messagebox.showerror direkt aus Thread (Bug #1)",
        )

    def test_screenshots_proc_wait_called_on_exception(self):
        """Bug #3: proc.wait() muss nach proc.terminate() im Fehlerfall aufgerufen werden."""
        done, _ = self._reset_after()

        fake_proc = MagicMock()

        with patch("subprocess.Popen", return_value=fake_proc), \
             patch("time.sleep", side_effect=RuntimeError("disk-io-error")), \
             patch("os.path.exists", return_value=True):
            self.app.run_screenshots()
            done.wait(timeout=3.0)

        fake_proc.terminate.assert_called_once()
        fake_proc.wait.assert_called()


class TestExceptionHandlerLambdas(unittest.TestCase):
    """Bug #4: except Exception as e in Hintergrundthreads -- Lambda darf e nicht direkt referenzieren."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.app = _minimal_app()
        except Exception as err:
            raise unittest.SkipTest(f"Tkinter GUI display unavailable: {err}")
        cls.app.script_path.set("/fake/script.py")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "app"):
            try:
                cls.app.destroy()
            except Exception:
                pass

    def test_build_exe_exception_lambda_callable_without_name_error(self):
        """Bug #4: Lambda im except Exception as e:-Block von build_exe muss NameError-frei aufrufbar sein."""
        after_calls = []
        done = threading.Event()

        def capture_after(delay, func, *args):
            after_calls.append(func)
            done.set()

        self.app.after = capture_after

        with patch("WindowsStorePublisher_3.ProgressDialog", return_value=MagicMock()), \
             patch.object(self.app, "get_build_interpreter", return_value=sys.executable), \
             patch("subprocess.run", side_effect=RuntimeError("forced")), \
             patch("tkinter.messagebox.askyesno", return_value=True), \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"):
            self.app.build_exe()
            done.wait(timeout=5.0)

        self.assertTrue(after_calls, "self.after sollte vom Hintergrundthread aufgerufen worden sein")
        with patch("tkinter.messagebox.showerror"), patch("tkinter.messagebox.showinfo"):
            for fn in after_calls:
                try:
                    fn()
                except NameError as ne:
                    self.fail(f"Lambda loeste NameError aus: {ne} -- Bug #4 nicht behoben")
                except Exception:
                    pass  # andere Exceptions sind OK


if __name__ == "__main__":
    unittest.main()
