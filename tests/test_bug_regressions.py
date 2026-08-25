"""Regressionstests — bugfix-library-transfer 2026-06-21."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import manage_translations as mt
import WindowsStorePublisher_3 as wsp


class _StringVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value


class TestU2TranslatorCode(unittest.TestCase):
    """BUG-U2: translator_code-Template hatte json.load ohne JSONDecodeError-Handler."""

    def test_translator_code_template_has_json_error_handler(self):
        """translator_code-String muss JSONDecodeError-Handler für json.load enthalten."""
        src = (Path(__file__).parent.parent / "WindowsStorePublisher_3.py").read_text(encoding="utf-8")
        idx = src.find("translator_code")
        self.assertGreater(idx, 0, "translator_code-Definition nicht gefunden")
        template = src[idx:idx + 2000]
        self.assertIn("json.JSONDecodeError", template,
                      "translator_code-Template ohne JSONDecodeError-Handler — BUG-U2")


class TestU2ManageTranslations(unittest.TestCase):
    """BUG-U2: manage_translations lud korrupte JSON ohne JSONDecodeError-Handler."""

    def test_corrupted_json_does_not_raise(self):
        """Korrupte translations.json darf keine unkontrollierte Exception werfen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            locales_dir = os.path.join(tmpdir, "locales")
            os.makedirs(locales_dir)
            with open(os.path.join(locales_dir, "translations.json"), "w", encoding="utf-8") as f:
                f.write("{corrupted json")
            try:
                mt.manage_translations(tmpdir)
            except json.JSONDecodeError:
                self.fail("JSONDecodeError nicht gefangen — BUG-U2 in manage_translations")


class TestD3SubprocessTimeout(unittest.TestCase):
    """BUG-D3: PyInstaller version check ohne timeout= konnte GUI-Thread blockieren."""

    def test_pyinstaller_version_check_has_timeout(self):
        """subprocess.run für PyInstaller --version muss timeout= enthalten."""
        src = (Path(__file__).parent.parent / "WindowsStorePublisher_3.py").read_text(encoding="utf-8")
        idx = src.find('"--version"')
        self.assertGreater(idx, 0, "PyInstaller --version Aufruf nicht gefunden")
        snippet = src[idx:idx + 300]
        self.assertIn("timeout", snippet,
                      "subprocess.run für PyInstaller --version ohne timeout= — BUG-D3")


class TestOutputDirectorySafety(unittest.TestCase):
    """Bugsearch: Profil-Appnamen dürfen den Output-Root nicht als Löschziel umbiegen."""

    def test_package_dir_never_uses_traversal_app_name_as_output_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = wsp.StorePackagerApp.__new__(wsp.StorePackagerApp)
            app.output_dir = _StringVar(tmpdir)
            app.app_name = _StringVar("..")

            package_dir = Path(app.package_dir()).resolve(strict=False)

            self.assertNotEqual(package_dir, Path(tmpdir).resolve(strict=False))
            self.assertEqual(package_dir.parent, Path(tmpdir).resolve(strict=False))
            self.assertEqual(package_dir.name, "App")

    def test_package_dir_preserves_plain_display_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = wsp.StorePackagerApp.__new__(wsp.StorePackagerApp)
            app.output_dir = _StringVar(tmpdir)
            app.app_name = _StringVar("SQLite Viewer Pro")

            self.assertEqual(Path(app.package_dir()).name, "SQLite Viewer Pro")


if __name__ == "__main__":
    unittest.main()
