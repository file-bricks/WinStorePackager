"""Tests für which()-Hilfsfunktion in WindowsStorePublisher_3.py (Bug #5)."""
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import WindowsStorePublisher_3 as _wsp


class TestWhichFunction(unittest.TestCase):
    """Bug #5: which() darf .exe-Dateien auf Windows nicht doppelt erweitern."""

    def test_which_finds_exe_by_full_name(self):
        """which('prog.exe') findet prog.exe ohne Doppel-Extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_exe = os.path.join(tmpdir, "fake_tool.exe")
            Path(fake_exe).touch()
            if os.name != "nt":
                os.chmod(fake_exe, os.stat(fake_exe).st_mode | stat.S_IEXEC)

            original_path = os.environ.get("PATH", "")
            os.environ["PATH"] = tmpdir + os.pathsep + original_path
            try:
                result = _wsp.which("fake_tool.exe")
            finally:
                os.environ["PATH"] = original_path

        self.assertIsNotNone(result, "which() sollte fake_tool.exe finden")
        lower = (result or "").lower()
        self.assertFalse(
            lower.endswith(".exe.exe") or lower.endswith(".exe.bat"),
            f"Doppel-Extension gefunden: {result} — Bug #5 nicht behoben",
        )

    def test_which_returns_none_for_missing_program(self):
        """which() gibt None zurück wenn Programm nicht im PATH ist."""
        result = _wsp.which("hopefully_nonexistent_xyz9876543.exe")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
