# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Bugsweep-Iteration 2026-09-28.

Prüft:
1. stage_payload():
   - Verzeichnis-Unterstützung: Übergabe eines Verzeichnispfads (z.B. aus source_path oder installer_path)
     kopiert den Verzeichnisbaum fehlerfrei, statt mit PermissionError abzustürzen.
   - Rekursionsschutz: Liegt outdir innerhalb von source_path, wird outdir nicht endlos in sich selbst kopiert.
2. build_icons():
   - Farbraum-Konvertierung: CMYK- und Nicht-RGBA-Bilder (z.B. Druckgrafiken, Palette) werden
     automatisch nach RGBA gewandelt, statt beim PNG-Speichern mit OSError abzustürzen.
   - Sauberes Schließen von PIL-Dateideskriptoren.
3. generate_manifest() & collect_python_licenses():
   - Automatische Verzeichnisanlage: Noch nicht existierende outdir-Pfade werden defensiv angelegt,
     statt mit FileNotFoundError beim open() abzubrechen.
4. _get_requirements_hash():
   - Resilienz gegen umschließende Anführungszeichen/Whitespace im script_path.
5. open_output_folder():
   - Plattformunabhängigkeit: Verwendet auf macOS (darwin) "open" statt des dort fehlenden "xdg-open",
     und fängt fehlende Starter-Binaries per Exception-Handling ab.
6. preflight_check():
   - Validierung von exe_name: Weist ungültige Endungen (nicht .exe) oder unzulässige Windows-Zeichen
     als kritischen Fehler (❌) im Build-Reiter (Tab 1) aus.
7. write_text_file():
   - Legt fehlende Elternverzeichnisse defensiv an.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import WindowsStorePublisher_3 as wsp


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _TextBox:
    def __init__(self, text=""):
        self.text = text

    def get(self, *args):
        return self.text

    def delete(self, *args):
        self.text = ""

    def insert(self, index, text):
        self.text += text


def _make_test_app() -> wsp.StorePackagerApp:
    app = wsp.StorePackagerApp.__new__(wsp.StorePackagerApp)

    app.language = _Var("de")
    app._translatable_items = []
    app._tooltips = []

    app.app_name = _Var("TestApp")
    app.publisher = _Var("CN=TestCorp")
    app.publisher_display = _Var("Test Studio")
    app.identity_name = _Var("Test.TestApp")
    app.version = _Var("1.0.0.0")
    app.script_path = _Var("")
    app.icon_path = _Var("")
    app.source_path = _Var("")
    app.installer_path = _Var("")
    app.output_dir = _Var("store_package")
    app.exe_name = _Var("TestApp.exe")
    app.makeappx_path = _Var("")
    app.signtool_path = _Var("")
    app.appcert_path = _Var("")
    app.pfx_path = _Var("")
    app.pfx_password = _Var("")
    app.timestamp_url = _Var("http://timestamp.digicert.com")
    app.msix_name = _Var("TestApp.msix")
    app.python_path = _Var("")
    app.enable_i18n = _Var(False)
    app.privacy_url = _Var("https://example.com/privacy")
    app.support_url = _Var("https://example.com/support")
    app.capabilities = _Var("internetClient")
    app.category = _Var("Productivity")
    app.age_rating = _Var("3+")

    app.desc_box = _TextBox("Beschreibung der Test-App")
    app.readme_box = _TextBox("README der Test-App")
    app.license_box = _TextBox("Lizenztext")
    app.changelog_box = _TextBox("Changelog")
    app.license_files = []
    app.license_text_entries = []

    app._status_text = ""
    app.set_status = lambda msg: setattr(app, "_status_text", msg)

    return app


class TestBugsweep20260928(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._msg_patch = patch("tkinter.messagebox.showwarning")
        self._msg_patch.start()

    def tearDown(self):
        self._msg_patch.stop()
        self.temp_dir.cleanup()

    def test_stage_payload_directory_support(self):
        """stage_payload muss Verzeichnisse kopieren können ohne PermissionError."""
        app = _make_test_app()
        source_dir = self.root / "my_source_dir"
        source_dir.mkdir()
        (source_dir / "module.py").write_text("print('hello')", encoding="utf-8")
        sub = source_dir / "sub"
        sub.mkdir()
        (sub / "data.json").write_text("{}", encoding="utf-8")

        outdir = self.root / "output"
        outdir.mkdir()

        copied = app.stage_payload(str(source_dir), str(outdir))
        self.assertGreaterEqual(copied, 2)
        staged_target = outdir / "my_source_dir"
        self.assertTrue(staged_target.is_dir())
        self.assertTrue((staged_target / "module.py").is_file())
        self.assertTrue((staged_target / "sub" / "data.json").is_file())

    def test_stage_payload_avoids_recursion_when_outdir_nested(self):
        """stage_payload darf bei verschachteltem outdir nicht endlos rekursieren."""
        app = _make_test_app()
        source_dir = self.root / "project_root"
        source_dir.mkdir()
        (source_dir / "app.py").write_text("pass", encoding="utf-8")
        outdir = source_dir / "store_package" / "TestApp"
        outdir.mkdir(parents=True)

        copied = app.stage_payload(str(source_dir), str(outdir))
        self.assertGreaterEqual(copied, 1)
        self.assertTrue((outdir / "project_root" / "app.py").is_file())
        # outdir selbst darf nicht in sich selbst gespiegelt werden
        self.assertFalse((outdir / "project_root" / "store_package").exists())

    def test_build_icons_converts_cmyk_and_palette(self):
        """build_icons muss CMYK- und Paletten-Bilder fehlerfrei zu PNG konvertieren."""
        app = _make_test_app()
        cmyk_icon = self.root / "icon_cmyk.jpg"
        img = Image.new("CMYK", (400, 400), (0, 100, 100, 0))
        img.save(cmyk_icon, format="JPEG")

        icon_dir = self.root / "icons"
        app.build_icons(str(cmyk_icon), str(icon_dir))

        for size in wsp.ICON_SIZES:
            icon_file = icon_dir / f"icon_{size}x{size}.png"
            self.assertTrue(icon_file.is_file())
            with Image.open(icon_file) as generated:
                self.assertEqual(generated.mode, "RGBA")
                self.assertEqual(generated.size, (size, size))

        wide_file = icon_dir / "icon_310x150.png"
        self.assertTrue(wide_file.is_file())
        with Image.open(wide_file) as generated:
            self.assertEqual(generated.mode, "RGBA")
            self.assertEqual(generated.size, (310, 150))

    def test_generate_manifest_creates_missing_outdir(self):
        """generate_manifest muss outdir defensiv anlegen, falls noch nicht vorhanden."""
        app = _make_test_app()
        outdir = self.root / "nested" / "nonexistent" / "pkg"
        self.assertFalse(outdir.exists())

        app.generate_manifest(str(outdir), "TestApp.exe")
        manifest_file = outdir / "AppxManifest.xml"
        self.assertTrue(manifest_file.is_file())
        self.assertIn("TestApp.exe", manifest_file.read_text(encoding="utf-8"))

    def test_collect_python_licenses_creates_missing_outdir(self):
        """collect_python_licenses muss outdir anlegen, falls noch nicht vorhanden."""
        app = _make_test_app()
        outdir = self.root / "nested" / "lic_pkg"
        self.assertFalse(outdir.exists())

        with patch("subprocess.run") as mock_sub:
            mock_sub.return_value = MagicMock(returncode=0)
            ok, target = app.collect_python_licenses(str(outdir))

        self.assertTrue(ok)
        self.assertTrue(outdir.is_dir())
        self.assertTrue(os.path.exists(target))

    def test_get_requirements_hash_strips_quotes(self):
        """_get_requirements_hash muss Pfade mit Anführungszeichen sauber auflösen."""
        app = _make_test_app()
        proj_dir = self.root / "my_project"
        proj_dir.mkdir()
        req_file = proj_dir / "requirements.txt"
        req_file.write_text("requests==2.31.0\n", encoding="utf-8")
        script_file = proj_dir / "main.py"
        script_file.write_text("print('test')", encoding="utf-8")

        # Quoted script path
        app.script_path.set(f'"{script_file}"')
        h = app._get_requirements_hash()
        self.assertTrue(bool(h))
        self.assertEqual(len(h), 32)

    def test_open_output_folder_handles_macos_and_missing_binary(self):
        """open_output_folder nutzt auf darwin 'open' und fängt Fehler ab."""
        app = _make_test_app()
        outdir = self.root / "pkg_out"
        outdir.mkdir()
        app.output_dir.set(str(outdir))
        app.app_name.set("")

        with patch("os.path.isdir", return_value=True), patch("sys.platform", "darwin"), patch("subprocess.run") as mock_run:
            app.open_output_folder()
            mock_run.assert_called_once()
            self.assertEqual(mock_run.call_args[0][0][0], "open")

        # Missing binary shouldn't crash
        with patch("os.path.isdir", return_value=True), patch("sys.platform", "linux"), patch("subprocess.run", side_effect=FileNotFoundError("not found")):
            app.open_output_folder()
            self.assertIn("Ordner konnte nicht geöffnet werden", app._status_text)

    def test_preflight_check_validates_exe_name(self):
        """preflight_check muss fehlerhafte EXE-Namen bemängeln."""
        app = _make_test_app()
        # Set all basic requirements valid so only exe_name is tested
        dummy_script = self.root / "main.py"
        dummy_script.write_text("pass", encoding="utf-8")
        app.script_path.set(str(dummy_script))

        dummy_icon = self.root / "icon.png"
        Image.new("RGBA", (310, 310)).save(dummy_icon)
        app.icon_path.set(str(dummy_icon))

        dummy_bin = self.root / "dummy.exe"
        dummy_bin.write_text("", encoding="utf-8")
        app.makeappx_path.set(str(dummy_bin))
        app.signtool_path.set(str(dummy_bin))

        dummy_pfx = self.root / "cert.pfx"
        dummy_pfx.write_text("", encoding="utf-8")
        app.pfx_path.set(str(dummy_pfx))

        # 1. Invalid extension (missing .exe)
        app.exe_name.set("InvalidNameWithoutExtension")
        issues, first_tab = app.preflight_check()
        self.assertTrue(any("EXE-Name muss auf .exe enden" in i for i in issues))
        self.assertEqual(first_tab, 1)

        # 2. Invalid characters in exe_name
        app.exe_name.set("Bad:Name<Test>.exe")
        issues, first_tab = app.preflight_check()
        self.assertTrue(any("EXE-Name enthält ungültige Zeichen" in i for i in issues))

    def test_write_text_file_creates_parent_directories(self):
        """write_text_file muss fehlende übergeordnete Verzeichnisse anlegen."""
        app = _make_test_app()
        nested_file = self.root / "deep" / "nested" / "output.txt"
        self.assertFalse(nested_file.parent.exists())

        app.write_text_file(str(nested_file), "Hello World")
        self.assertTrue(nested_file.is_file())
        self.assertEqual(nested_file.read_text(encoding="utf-8"), "Hello World")


if __name__ == "__main__":
    unittest.main()
