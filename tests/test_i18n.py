import json
import tkinter as tk
import unittest
from pathlib import Path

from translator import TranslationSystem, detect_system_language, SUPPORTED_LANGUAGES
import WindowsStorePublisher_3 as _wsp


class TestTranslationSystem(unittest.TestCase):
    def setUp(self):
        self.locales_dir = Path(__file__).parent.parent / "locales"
        self.ts_de = TranslationSystem(default_lang="de", app_dir=Path(__file__).parent.parent)
        self.ts_en = TranslationSystem(default_lang="en", app_dir=Path(__file__).parent.parent)
        self.ts_es = TranslationSystem(default_lang="es", app_dir=Path(__file__).parent.parent)
        self.ts_zh = TranslationSystem(default_lang="zh", app_dir=Path(__file__).parent.parent)
        self.ts_ja = TranslationSystem(default_lang="ja", app_dir=Path(__file__).parent.parent)
        self.ts_ru = TranslationSystem(default_lang="ru", app_dir=Path(__file__).parent.parent)

    def test_translations_json_exists_and_valid_6_languages(self):
        json_path = self.locales_dir / "translations.json"
        self.assertTrue(json_path.exists(), "translations.json must exist")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertGreater(len(data), 50)
        for key, entry in data.items():
            for lang in SUPPORTED_LANGUAGES:
                self.assertIn(lang, entry, f"Language '{lang}' missing in key '{key}'")
                self.assertTrue(bool(entry[lang]), f"Language '{lang}' has empty translation for key '{key}'")

    def test_translation_all_6_languages(self):
        self.assertEqual(self.ts_de.t("Metadaten"), "Metadaten")
        self.assertEqual(self.ts_en.t("Metadaten"), "Metadata")
        self.assertEqual(self.ts_es.t("Metadaten"), "Metadatos")
        self.assertEqual(self.ts_zh.t("Metadaten"), "元数据")
        self.assertEqual(self.ts_ja.t("Metadaten"), "メタデータ")
        self.assertEqual(self.ts_ru.t("Metadaten"), "Метаданные")

        self.assertEqual(self.ts_de.t("Build-Einstellungen"), "Build-Einstellungen")
        self.assertEqual(self.ts_en.t("Build-Einstellungen"), "Build Settings")
        self.assertEqual(self.ts_es.t("Build-Einstellungen"), "Ajustes de compilación")
        self.assertEqual(self.ts_zh.t("Build-Einstellungen"), "构建设置")
        self.assertEqual(self.ts_ja.t("Build-Einstellungen"), "ビルド設定")
        self.assertEqual(self.ts_ru.t("Build-Einstellungen"), "Настройки сборки")

        self.assertEqual(self.ts_de.t("Store-Informationen"), "Store-Informationen")
        self.assertEqual(self.ts_en.t("Store-Informationen"), "Store Information")
        self.assertEqual(self.ts_es.t("Store-Informationen"), "Información de la tienda")
        self.assertEqual(self.ts_zh.t("Store-Informationen"), "商店信息")
        self.assertEqual(self.ts_ja.t("Store-Informationen"), "ストア情報")
        self.assertEqual(self.ts_ru.t("Store-Informationen"), "Информация о магазине")

        self.assertEqual(self.ts_de.t("Aktionen"), "Aktionen")
        self.assertEqual(self.ts_en.t("Aktionen"), "Actions")
        self.assertEqual(self.ts_es.t("Aktionen"), "Acciones")
        self.assertEqual(self.ts_zh.t("Aktionen"), "操作")
        self.assertEqual(self.ts_ja.t("Aktionen"), "アクション")
        self.assertEqual(self.ts_ru.t("Aktionen"), "Действия")

    def test_fallback_for_unknown_key(self):
        unknown = "ThisKeyDoesNotExistInTranslationFile123"
        self.assertEqual(self.ts_de.t(unknown), unknown)
        self.assertEqual(self.ts_en.t(unknown), unknown)
        self.assertEqual(self.ts_es.t(unknown), unknown)

    def test_fallback_chain(self):
        ts = TranslationSystem(default_lang="es", app_dir=Path(__file__).parent.parent)
        # Mock translation with missing 'es' but present 'en'
        ts.translations["CustomTestKey"] = {"de": "Deutscher Text", "en": "English Text", "es": ""}
        self.assertEqual(ts.t("CustomTestKey"), "English Text")

        # Mock translation with missing 'es' and 'en', but present 'de'
        ts.translations["CustomTestKey2"] = {"de": "Deutscher Text 2", "en": "", "es": ""}
        self.assertEqual(ts.t("CustomTestKey2"), "Deutscher Text 2")

    def test_language_switch(self):
        ts = TranslationSystem(default_lang="de", app_dir=Path(__file__).parent.parent)
        self.assertEqual(ts.get_language(), "de")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Preflight-Check")

        ts.set_language("en")
        self.assertEqual(ts.get_language(), "en")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Preflight Check")

        ts.set_language("es")
        self.assertEqual(ts.get_language(), "es")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Verificación previa")

        ts.set_language("zh")
        self.assertEqual(ts.get_language(), "zh")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. 预检检查")

        ts.set_language("ja")
        self.assertEqual(ts.get_language(), "ja")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. プリフライトチェック")

        ts.set_language("ru")
        self.assertEqual(ts.get_language(), "ru")
        self.assertEqual(ts.t("1. Preflight-Check"), "1. Предварительная проверка")

    def test_supported_languages_list(self):
        ts = TranslationSystem(default_lang="de", app_dir=Path(__file__).parent.parent)
        self.assertEqual(ts.get_supported_languages(), ["de", "en", "es", "zh", "ja", "ru"])

    def test_detect_system_language(self):
        lang = detect_system_language()
        self.assertIn(lang, SUPPORTED_LANGUAGES)


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

        # Switch through all 6 languages and verify translations
        for lang in ("en", "es", "zh", "ja", "ru", "de"):
            _wsp.get_translator().set_language(lang)
            self.app.language.set(lang)
            self.app.refresh_ui_language()

            for widget, prop, key in self.app._translatable_items:
                translated = _wsp._t(key)
                self.assertEqual(widget.cget(prop), translated)


if __name__ == "__main__":
    unittest.main()
