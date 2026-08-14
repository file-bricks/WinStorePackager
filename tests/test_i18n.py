import json
import tkinter as tk
import unittest
from pathlib import Path

from translator import TranslationSystem, detect_system_language
import WindowsStorePublisher_3 as _wsp


class TestTranslationSystem(unittest.TestCase):
    def setUp(self):
        self.locales_dir = Path(__file__).parent.parent / "locales"
        self.ts_de = TranslationSystem(default_lang="de", app_dir=Path(__file__).parent.parent)
        self.ts_en = TranslationSystem(default_lang="en", app_dir=Path(__file__).parent.parent)

    def test_translations_json_exists_and_valid(self):
        json_path = self.locales_dir / "translations.json"
        self.assertTrue(json_path.exists(), "translations.json must exist")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertGreater(len(data), 50)
        for key, entry in data.items():
            self.assertIn("de", entry)
            self.assertIn("en", entry)
            self.assertTrue(bool(entry["de"]))
            self.assertTrue(bool(entry["en"]))

    def test_translation_de_and_en(self):
        self.assertEqual(self.ts_de.t("Metadaten"), "Metadaten")
        self.assertEqual(self.ts_en.t("Metadaten"), "Metadata")

        self.assertEqual(self.ts_de.t("Build-Einstellungen"), "Build-Einstellungen")
        self.assertEqual(self.ts_en.t("Build-Einstellungen"), "Build Settings")

        self.assertEqual(self.ts_de.t("Store-Informationen"), "Store-Informationen")
        self.assertEqual(self.ts_en.t("Store-Informationen"), "Store Information")

        self.assertEqual(self.ts_de.t("Aktionen"), "Aktionen")
        self.assertEqual(self.ts_en.t("Aktionen"), "Actions")

    def test_fallback_for_unknown_key(self):
        unknown = "ThisKeyDoesNotExistInTranslationFile123"
        self.assertEqual(self.ts_de.t(unknown), unknown)
        self.assertEqual(self.ts_en.t(unknown), unknown)

    def test_language_switch(self):
        ts = TranslationSystem(default_lang="de", app_dir=Path(__file__).parent.parent)
        self.assertEqual(ts.get_language(), "de")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Preflight-Check")

        ts.set_language("en")
        self.assertEqual(ts.get_language(), "en")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Preflight Check")

    def test_detect_system_language(self):
        lang = detect_system_language()
        self.assertIn(lang, ("de", "en"))


def _create_test_app():
    app = _wsp.StorePackagerApp.__new__(_wsp.StorePackagerApp)
    tk.Tk.__init__(app)
    app.withdraw()

    app.app_name = tk.StringVar(value="TestApp")
    app.publisher = tk.StringVar(value="CN=Test")
    app.publisher_display = tk.StringVar(value="Test Studio")
    app.identity_name = tk.StringVar(value="Test.TestApp")
    app.version = tk.StringVar(value="1.0.0.0")
    app.script_path = tk.StringVar()
    app.icon_path = tk.StringVar()
    app.source_path = tk.StringVar()
    app.installer_path = tk.StringVar()
    app.output_dir = tk.StringVar(value="store_package")
    app.exe_name = tk.StringVar(value="TestApp.exe")
    app.makeappx_path = tk.StringVar()
    app.signtool_path = tk.StringVar()
    app.appcert_path = tk.StringVar()
    app.pfx_path = tk.StringVar()
    app.pfx_password = tk.StringVar()
    app.timestamp_url = tk.StringVar(value="http://timestamp.example")
    app.msix_name = tk.StringVar(value="TestApp.msix")
    app.python_path = tk.StringVar()
    app.enable_i18n = tk.BooleanVar(value=False)
    app.privacy_url = tk.StringVar(value="https://example.test/privacy")
    app.support_url = tk.StringVar(value="https://example.test/support")
    app.capabilities = tk.StringVar(value="internetClient")
    app.category = tk.StringVar(value="Productivity")
    app.age_rating = tk.StringVar(value="3+")
    app.language = tk.StringVar(value="de")
    app._translatable_items = []
    app.lang_menu = None
    app.readme_box = None
    app.license_box = None
    app.desc_box = None
    return app


class TestUiLanguageSwitching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.app = _create_test_app()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tkinter display unavailable: {exc}") from exc

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_dynamic_ui_language_refresh(self):
        # Build tabs
        tab1 = tk.Frame(self.app)
        self.app.build_metadata_tab(tab1)
        tab2 = tk.Frame(self.app)
        self.app.build_actions_tab(tab2)

        # Confirm German texts registered
        self.assertGreater(len(self.app._translatable_items), 10)

        # Switch to English
        _wsp.get_translator().set_language("en")
        self.app.language.set("en")
        self.app.refresh_ui_language()

        # Check translatable items updated
        for widget, prop, key in self.app._translatable_items:
            translated = _wsp._t(key)
            self.assertEqual(widget.cget(prop), translated)

        # Switch back to German
        _wsp.get_translator().set_language("de")
        self.app.language.set("de")
        self.app.refresh_ui_language()

        for widget, prop, key in self.app._translatable_items:
            translated = _wsp._t(key)
            self.assertEqual(widget.cget(prop), translated)


if __name__ == "__main__":
    unittest.main()
