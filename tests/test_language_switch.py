"""Regressionstests — WELLE-1-USERTEST U2 (2026-07-23), Sprachumschaltung.

Befund: Es gab in der App KEINE sichtbare Möglichkeit, Deutsch/Englisch
umzustellen, obwohl `locales/translations.json` + `translator.py` bereits
vorhanden waren -- die Infrastruktur war nie an ein GUI-Element angebunden.
Diese Tests decken die neue Sprachumschaltung ab: Persistenz in
settings_store_packager.json, Zuordnung Anzeige-Name <-> Sprachcode, und dass
die live nachgezogenen "Chrome"-Texte (Fenstertitel, Reiter) tatsächlich in
translations.json mit einer echten (nicht-leeren) englischen Übersetzung
hinterlegt sind.

Tk-Instanziierung folgt dem in tests/test_threading_bugs.py etablierten
Muster (StorePackagerApp.__new__() statt vollem StorePackagerApp()), geht
aber noch einen Schritt weiter: EINE gemeinsame App-Instanz für das gesamte
Modul statt einer neuen pro Testmethode. Grund (empirisch): Jede zusätzliche
tk.Tk()-Neuinstanziierung im selben Prozess erhöht auf diesem System das
Risiko einer spaeteren TclError ("couldn't read ttk/progress.tcl") in ANDEREN
Testdateien, die nach diesem Modul laufen (test_threading_bugs.py erzeugt
selbst mehrere Tk-Roots) -- die Tcl/Tk-Installation vertraegt offenbar nur
eine begrenzte Zahl von Root-Neuerzeugungen pro Prozess. Ein gemeinsames
App-Objekt haelt den Beitrag dieses Moduls zu diesem Budget minimal.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import ttk
import WindowsStorePublisher_3 as _wsp

REPO_ROOT = Path(__file__).parent.parent

# EINE gemeinsame App-Instanz fuer das ganze Modul (siehe Modul-Docstring:
# jede zusaetzliche tk.Tk()-Neuinstanziierung ist auf diesem System ein
# Risiko fuer TclError in NACHFOLGENDEN Testdateien).
_shared_app = None


def _minimal_app(build_gui=False):
    """Liefert eine (modulweit wiederverwendete) StorePackagerApp-Instanz ohne
    den vollen Konstruktor (kein load_settings()/autodetect_sdk_tools() beim
    Erzeugen) -- optional mit echtem build_gui()-Aufruf fuer Widget-Existenz-
    Tests. Wird NUR beim ersten Aufruf tatsaechlich ein tk.Tk() erzeugt."""
    global _shared_app
    if _shared_app is not None:
        if build_gui and _shared_app.notebook is None:
            _shared_app.build_gui()
        return _shared_app

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

    # Sprachumschaltung (U2)
    app.translator = _wsp.TranslationSystem(default_lang="de", app_dir=REPO_ROOT)
    app.app_language = tk.StringVar(value=_wsp.LANGUAGES["de"])
    app.notebook = None

    if build_gui:
        app.build_gui()

    _shared_app = app
    return app


class TestLanguageMapping(unittest.TestCase):
    """LANGUAGES-Konstante: Anzeige-Name (Combobox) <-> interner Sprachcode."""

    def test_languages_contains_de_and_en(self):
        self.assertEqual(_wsp.LANGUAGES.get("de"), "Deutsch")
        self.assertEqual(_wsp.LANGUAGES.get("en"), "English")


class TestLanguagePersistence(unittest.TestCase):
    """Sprachwahl muss in settings_store_packager.json persistiert und beim
    nächsten Start wieder geladen werden (BUG U2: bisher gar nicht vorhanden)."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.settings_file = os.path.join(self.tmpdir.name, "settings_store_packager.json")

    def tearDown(self):
        self.tmpdir.cleanup()
        # Geteilte App-Instanz (siehe Modul-Docstring) auf Deutsch zuruecksetzen,
        # damit Tests unabhaengig von der Ausfuehrungsreihenfolge starten.
        if _shared_app is not None:
            _shared_app.app_language.set(_wsp.LANGUAGES["de"])
            _shared_app.translator.set_language("de")

    def test_language_change_persists_to_settings_file(self):
        app = _minimal_app()
        app.app_language.set(_wsp.LANGUAGES["en"])
        with patch.object(_wsp, "SETTINGS_FILE", self.settings_file), \
             patch.object(_wsp.messagebox, "showinfo"):
            app.on_language_change()

        self.assertTrue(os.path.exists(self.settings_file),
                         "Sprachwechsel hat keine Settings-Datei geschrieben")
        with open(self.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("language"), "en",
                          "Sprachcode 'en' wurde nicht persistiert — BUG U2 Regression")

    def test_language_change_does_not_touch_keyring_or_full_save_dialog(self):
        """on_language_change() nutzt bewusst NICHT den vollen save_settings()-Pfad
        (kein Keyring-Zugriff, kein zusaetzlicher 'Gespeichert'-Dialog)."""
        app = _minimal_app()
        app.app_language.set(_wsp.LANGUAGES["en"])
        with patch.object(_wsp, "SETTINGS_FILE", self.settings_file), \
             patch.object(_wsp.messagebox, "showinfo"), \
             patch.object(_wsp.keyring, "set_password") as mock_set_password:
            app.on_language_change()
        mock_set_password.assert_not_called()

    def test_saved_language_is_reloaded_on_next_start(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump({"language": "en"}, f)

        app = _minimal_app()
        with patch.object(_wsp, "SETTINGS_FILE", self.settings_file):
            app.load_settings()
        self.assertEqual(app.app_language.get(), _wsp.LANGUAGES["en"],
                          "Gespeicherte Sprache 'en' wurde beim Start nicht übernommen")
        self.assertEqual(app.translator.get_language(), "en")


class TestLanguageComboboxVisible(unittest.TestCase):
    """U2 verlangt eine SICHTBARE Umschaltung -- keine versteckte Einstellung."""

    def test_language_combobox_present_in_build_tab(self):
        app = _minimal_app(build_gui=True)
        found = self._find_combobox_bound_to(app, app.app_language)
        self.assertIsNotNone(found, "Kein sichtbares Combobox-Widget für die Sprachumschaltung gefunden")

    def _find_combobox_bound_to(self, widget, string_var):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Combobox):
                try:
                    if str(child.cget("textvariable")) == str(string_var):
                        return child
                except tk.TclError:
                    pass
            result = self._find_combobox_bound_to(child, string_var)
            if result is not None:
                return result
        return None


class TestTranslationsCoverLiveChromeStrings(unittest.TestCase):
    """Die live nachgezogenen 'Chrome'-Texte (Titel, Reiter, Sprachwechsel-Dialog)
    müssen eine ECHTE (nicht-leere) englische Übersetzung haben, sonst zeigt
    Englisch trotz Umschaltung weiterhin deutschen Text (Fallback auf den Key)."""

    LIVE_CHROME_KEYS = [
        "Windows Store Packager v2.3 (Auto-Setup)",
        "Metadaten",
        "Build-Einstellungen",
        "Store-Informationen",
        "Aktionen",
        "Sprache geändert",
        "Titel und Reiter wurden aktualisiert. Für die vollständige Wirkung auf "
        "alle Texte bitte die Anwendung neu starten.",
    ]

    @classmethod
    def setUpClass(cls):
        with open(REPO_ROOT / "locales" / "translations.json", "r", encoding="utf-8") as f:
            cls.translations = json.load(f)

    def test_all_live_chrome_keys_have_non_empty_english_translation(self):
        for key in self.LIVE_CHROME_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, self.translations,
                              f"'{key}' fehlt in locales/translations.json")
                en = self.translations[key].get("en", "")
                self.assertTrue(en, f"'{key}' hat keine (oder leere) englische Übersetzung")


if __name__ == "__main__":
    unittest.main()
