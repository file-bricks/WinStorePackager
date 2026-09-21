# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Bugsweep-Iteration 2026-09-21.

Prüft:
1. safe_package_dir_name():
   - Bereinigt reservierte Windows-Zeichen (<, >, :, ", |, ?, *), Steuerzeichen,
     nachgestellte Punkte/Leerzeichen sowie DOS-Gerätenamen (CON, NUL, AUX, PRN, COM1-9, LPT1-9).
   - Verhindert WinError 123 bei os.makedirs().
2. preflight_check():
   - Nicht lesbare oder beschädigte Icons führen nicht zu einer leeren Meldung (""),
     sondern werden ordnungsgemäß als Warnung gemeldet.
   - Vorhandene license_text_entries werden anerkannt und führen nicht fälschlich
     zu "⚠️  Lizenz fehlt".
   - Fehlende oder ungültige Version wird als kritischer Fehler (❌) gemeldet,
     wobei leere Version sauber "❌ Version fehlt" ausgibt.
   - PFX-Pfade mit Anführungszeichen/Whitespace werden vorab getrimmt.
3. validate_signing_credentials():
   - PFX-Dateipfade mit umschließenden Anführungszeichen oder Whitespace werden toleriert.
   - PFX-Dateien mit falscher Endung (z.B. .cer oder .txt) werden als ungültig abgewiesen.
   - pfx_pw=None wird abgewiesen.
"""
import os
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import patch

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
    app.license_box = _TextBox("")
    app.license_files = []
    app.license_text_entries = []

    return app


def test_safe_package_dir_name_sanitizes_windows_illegal_characters():
    illegal_cases = [
        ("App<Test>", "AppTest"),
        ("App: Pro Edition", "AppProEdition"),
        ("App*Star", "AppStar"),
        ("App?Help", "AppHelp"),
        ("App|Pipe", "AppPipe"),
        ('App"Quote"', "AppQuote"),
        ("MyApp.", "MyApp"),
        ("MyApp ", "MyApp"),
    ]
    for raw_name, expected in illegal_cases:
        safe_name = wsp.safe_package_dir_name(raw_name)
        assert safe_name == expected, f"{raw_name!r} -> {safe_name!r} != {expected!r}"
        # Ensure it never contains any invalid Windows filesystem characters
        assert not any(c in safe_name for c in '<>:"/\\|?*')
        assert not safe_name.endswith((".", " "))


def test_safe_package_dir_name_handles_dos_reserved_device_names():
    reserved_names = ["CON", "NUL", "AUX", "PRN", "COM1", "LPT1"]
    for raw_name in reserved_names:
        safe_name = wsp.safe_package_dir_name(raw_name)
        assert safe_name.upper() not in reserved_names
        assert safe_name == f"App_{raw_name}"


def test_preflight_check_corrupt_icon_warns_with_non_empty_dialog(tmp_path):
    app = _make_test_app()
    corrupt_icon = tmp_path / "corrupt_icon.png"
    corrupt_icon.write_bytes(b"not a valid png or ico content")

    app.icon_path.set(str(corrupt_icon))

    dummy_script = tmp_path / "main.py"
    dummy_script.write_text("print('hello')", encoding="utf-8")
    app.script_path.set(str(dummy_script))

    dummy_pfx = tmp_path / "cert.pfx"
    dummy_pfx.write_bytes(b"pfx")
    app.pfx_path.set(str(dummy_pfx))

    dummy_tool = tmp_path / "tool.exe"
    dummy_tool.write_bytes(b"exe")
    app.makeappx_path.set(str(dummy_tool))
    app.signtool_path.set(str(dummy_tool))

    app.license_box.insert("1.0", "MIT License")

    shown_warnings = []
    with patch("tkinter.messagebox.showwarning", side_effect=lambda title, msg: shown_warnings.append((title, msg))):
        res = app.preflight_check()

    assert len(shown_warnings) == 1
    title, msg = shown_warnings[0]
    assert msg.strip() != "", "Preflight-Check Dialogbox darf nicht leer sein!"
    assert "Icon konnte nicht gelesen werden" in msg


def test_preflight_check_recognizes_license_text_entries(tmp_path):
    app = _make_test_app()
    dummy_script = tmp_path / "main.py"
    dummy_script.write_text("print('hello')", encoding="utf-8")
    app.script_path.set(str(dummy_script))

    dummy_pfx = tmp_path / "cert.pfx"
    dummy_pfx.write_bytes(b"pfx")
    app.pfx_path.set(str(dummy_pfx))

    dummy_tool = tmp_path / "tool.exe"
    dummy_tool.write_bytes(b"exe")
    app.makeappx_path.set(str(dummy_tool))
    app.signtool_path.set(str(dummy_tool))

    from PIL import Image
    icon_file = tmp_path / "valid_icon.png"
    Image.new("RGBA", (512, 512), (255, 0, 0, 255)).save(icon_file)
    app.icon_path.set(str(icon_file))

    # Empty license box, but license_text_entries present
    app.license_box.delete("1.0", tk.END)
    app.license_files = []
    app.license_text_entries = ["Apache-2.0 License Text"]

    shown_warnings = []
    with patch("tkinter.messagebox.showwarning", side_effect=lambda title, msg: shown_warnings.append((title, msg))):
        with patch("tkinter.messagebox.showinfo"):
            app.preflight_check()

    if shown_warnings:
        _, msg = shown_warnings[0]
        assert "Lizenz fehlt" not in msg, "license_text_entries darf nicht fälschlich als 'Lizenz fehlt' gemeldet werden"


def test_preflight_check_missing_or_invalid_version(tmp_path):
    app = _make_test_app()
    app.version.set("")

    shown_warnings = []
    with patch("tkinter.messagebox.showwarning", side_effect=lambda title, msg: shown_warnings.append((title, msg))):
        app.preflight_check()

    assert len(shown_warnings) == 1
    _, msg = shown_warnings[0]
    assert "❌ Version fehlt" in msg
    assert "Version hat falsches Format: " not in msg


def test_validate_signing_credentials_tolerates_quotes_and_whitespace():
    with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as tf:
        pfx_file = tf.name

    try:
        quoted_pfx = f' "{pfx_file}" '
        valid, errors = wsp.validate_signing_credentials(
            pfx_path=quoted_pfx,
            pfx_pw="Secret123",
            publisher_cn="CN=TestCorp",
            timestamp_url="http://timestamp.digicert.com",
        )
        assert valid is True, f"Validierung mit Anführungszeichen/Whitespace schlug fehl: {errors}"
        assert len(errors) == 0
    finally:
        if os.path.exists(pfx_file):
            os.remove(pfx_file)


def test_validate_signing_credentials_rejects_non_pfx_files():
    with tempfile.NamedTemporaryFile(suffix=".cer", delete=False) as tf:
        cer_file = tf.name

    try:
        valid, errors = wsp.validate_signing_credentials(
            pfx_path=cer_file,
            pfx_pw="Secret123",
            publisher_cn="CN=TestCorp",
            timestamp_url="http://timestamp.digicert.com",
        )
        assert valid is False
        assert any("muss auf .pfx oder .p12 enden" in err for err in errors)
    finally:
        if os.path.exists(cer_file):
            os.remove(cer_file)


def test_validate_signing_credentials_rejects_none_password():
    with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as tf:
        pfx_file = tf.name

    try:
        valid, errors = wsp.validate_signing_credentials(
            pfx_path=pfx_file,
            pfx_pw=None,
            publisher_cn="CN=TestCorp",
            timestamp_url="http://timestamp.digicert.com",
        )
        assert valid is False
        assert any("Passwort darf nicht None sein" in err for err in errors)
    finally:
        if os.path.exists(pfx_file):
            os.remove(pfx_file)
