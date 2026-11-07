"""
Vertragstests für Tier-2 Windows Store Packaging & 6-Sprachen-Materialien (Policy P-006).
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_STORE_DIR = PROJECT_ROOT / "releases" / "windowsstore"
TIER2_LANGS = ("de", "en", "es", "zh", "ja", "ru")
TIER2_STORE_LANGS = ("de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU")


class TestStoreMaterials(unittest.TestCase):

    def setUp(self):
        self.store_pkg_path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(self.store_pkg_path.is_file(), "store_package.json fehlt")
        self.store_pkg = json.loads(self.store_pkg_path.read_text(encoding="utf-8"))

        self.store_settings_path = WINDOWS_STORE_DIR / "store_settings.json"
        self.assertTrue(self.store_settings_path.is_file(), "releases/windowsstore/store_settings.json fehlt")
        self.store_settings = json.loads(self.store_settings_path.read_text(encoding="utf-8"))

    def test_store_package_declares_six_tier2_languages(self):
        langs = self.store_pkg.get("languages", [])
        for expected in TIER2_STORE_LANGS:
            self.assertIn(expected, langs, f"Fehlende Tier-2 Sprache: {expected}")

    def test_store_package_short_descriptions_length(self):
        for lang in TIER2_LANGS:
            key = f"description_{lang}"
            self.assertIn(key, self.store_pkg, f"Fehlende Kurzbeschreibung '{key}'")
            desc = self.store_pkg[key]
            self.assertIsInstance(desc, str)
            self.assertTrue(len(desc) > 0, f"Kurzbeschreibung '{key}' ist leer")
            self.assertLessEqual(len(desc), 100, f"Kurzbeschreibung '{key}' überschreitet 100 Zeichen: {len(desc)}")

    def test_store_package_keywords_policy_compliance(self):
        for lang in TIER2_LANGS:
            key = f"keywords_{lang}"
            self.assertIn(key, self.store_pkg, f"Fehlende Keywords '{key}'")
            kws = self.store_pkg[key]
            self.assertIsInstance(kws, list)
            self.assertGreaterEqual(len(kws), 1, f"Keywords '{key}' leer")
            self.assertLessEqual(len(kws), 7, f"Keywords '{key}' überschreitet Maximum von 7 (Policy 10.1.3)")
            for kw in kws:
                self.assertLessEqual(len(kw), 30, f"Keyword '{kw}' in '{key}' überschreitet 30 Zeichen")

    def test_store_settings_in_sync_with_store_package(self):
        self.assertEqual(self.store_pkg["app_name"], self.store_settings["app_name"])
        self.assertEqual(self.store_pkg["version"], self.store_settings["version"])
        self.assertEqual(self.store_pkg["publisher"], self.store_settings["publisher"])
        self.assertEqual(self.store_pkg["publisher_display"], self.store_settings["publisher_display"])
        self.assertEqual(self.store_pkg["identity_name"], self.store_settings["identity_name"])
        self.assertEqual(self.store_pkg["privacy_url"], self.store_settings["privacy_url"])
        self.assertEqual(self.store_pkg["support_url"], self.store_settings["support_url"])
        self.assertEqual(self.store_pkg["languages"], self.store_settings["languages"])

    def test_staged_store_listings_exist_and_non_empty(self):
        for lang in TIER2_LANGS:
            listing_file = WINDOWS_STORE_DIR / f"store_listing_{lang}.md"
            self.assertTrue(listing_file.is_file(), f"Staged Listing fehlt: {listing_file.name}")
            content = listing_file.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 100, f"Staged Listing zu kurz: {listing_file.name}")

    def test_store_listing_markdown_contains_all_six_sections(self):
        listing_md = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(listing_md.is_file(), "STORE_LISTING.md fehlt")
        text = listing_md.read_text(encoding="utf-8")
        for section in ("Deutsch", "English", "Español", "简体中文", "日本語", "Русский"):
            self.assertIn(f"## {section}", text, f"Abschnitt '## {section}' fehlt in STORE_LISTING.md")

    def test_wack_protocol_and_build_docs_exist(self):
        build_md = WINDOWS_STORE_DIR / "BUILD.md"
        wack_md = WINDOWS_STORE_DIR / "WACK_PROTOCOL.md"
        self.assertTrue(build_md.is_file(), "releases/windowsstore/BUILD.md fehlt")
        self.assertTrue(wack_md.is_file(), "releases/windowsstore/WACK_PROTOCOL.md fehlt")


if __name__ == "__main__":
    unittest.main()
