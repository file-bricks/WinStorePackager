"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 2.0.0 (Standardisiert gemäß P-006 / Tier-2-Mehrsprachigkeit)
Unterstützte Sprachen: DE, EN, ES, ZH (Vereinfacht), JA, RU

Verwendung:
-----------
from translator import TranslationSystem, detect_system_language, SUPPORTED_LANGUAGES

translator = TranslationSystem('de')
label.setText(translator.t('Datei öffnen'))
translator.set_language('en')
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional

SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")
DEFAULT_LANGUAGE = "de"

LANGUAGE_NAMES = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "zh": "简体中文",
    "ja": "日本語",
    "ru": "Русский",
}


def detect_system_language() -> str:
    """
    Erkennt die Systemsprache (Windows UI Language oder Locale) mit Fallback 'de'.
    Unterstützt Standard-Sprachen: 'de', 'en', 'es', 'zh', 'ja', 'ru'.

    Returns:
        Sprachcode ('de', 'en', 'es', 'zh', 'ja', 'ru')
    """
    import sys
    try:
        if sys.platform.startswith("win"):
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF
            lang_map = {
                0x07: "de",  # German
                0x09: "en",  # English
                0x0A: "es",  # Spanish
                0x04: "zh",  # Chinese
                0x11: "ja",  # Japanese
                0x19: "ru",  # Russian
            }
            if lang_id in lang_map:
                return lang_map[lang_id]
            return "en"
    except Exception:
        pass
    try:
        import locale
        loc = (locale.getdefaultlocale()[0] or "").lower()
        if loc.startswith("de"):
            return "de"
        if loc.startswith("es"):
            return "es"
        if loc.startswith("zh"):
            return "zh"
        if loc.startswith("ja"):
            return "ja"
        if loc.startswith("ru"):
            return "ru"
        if loc.startswith("en"):
            return "en"
    except Exception:
        pass
    return "de"


class TranslationSystem:
    """Multi-Language Support System v2.0 (DE, EN, ES, ZH, JA, RU)"""

    def __init__(self, default_lang: str = 'de', app_dir: Optional[Path] = None, auto_register: bool = False):
        """
        Initialisiert das Translation-System.

        Args:
            default_lang: Standard-Sprache ('de', 'en', 'es', 'zh', 'ja', 'ru')
            app_dir: Verzeichnis der Anwendung (default: Verzeichnis dieser Datei)
            auto_register: Ob unbekannte deutsche Keys automatisch in translations.json eingetragen werden sollen.
        """
        if default_lang not in SUPPORTED_LANGUAGES:
            default_lang = DEFAULT_LANGUAGE
        self.current_lang = default_lang
        self.auto_register = auto_register

        if app_dir is None:
            app_dir = Path(__file__).parent.resolve()
        self.app_dir = Path(app_dir)

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "oeffnen", "speichern",
            "schliessen", "einstellungen", "abbrechen", "ok", "ja", "nein",
            "start", "stop", "pause", "fortsetzen", "laden", "aktualisieren",
            "filter", "fehler", "export", "import", "optionen", "anzeigen",
            "wählen", "erfolgreich", "hinweis", "warnung", "ausgabeordner",
        ]

        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self):
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def t(self, key: str, **kwargs) -> str:
        """
        Übersetzt einen Key in die aktuelle Sprache mit einer 4-stufigen Fallback-Kette:
        1. Aktuelle Sprache (z.B. es, zh, ja, ru)
        2. Englisch ('en')
        3. Deutsch ('de')
        4. Original Key

        Args:
            key: Translation-Key (oft der deutsche Originaltext)
            **kwargs: Optionale Formatierungsargumente

        Returns:
            Übersetzter Text oder Key als Fallback
        """
        res = key
        if key in self.translations:
            entry = self.translations[key]
            val = entry.get(self.current_lang)
            if val:
                res = val
            elif entry.get("en"):
                res = entry["en"]
            elif entry.get("de"):
                res = entry["de"]
            else:
                res = key
        elif self.auto_register and self._is_german(key):
            self.translations[key] = {lang: (key if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
            self._save_translations()
            res = key

        if kwargs:
            try:
                return res.format(**kwargs)
            except Exception:
                return res
        return res

    def set_language(self, lang: str):
        """Setzt die aktive Sprache, wenn sie in SUPPORTED_LANGUAGES enthalten ist."""
        if lang in SUPPORTED_LANGUAGES:
            self.current_lang = lang

    def get_language(self) -> str:
        """Gibt die aktuell aktive Sprache zurück."""
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        """Gibt die Liste aller unterstützten Sprachcodes zurück."""
        return list(SUPPORTED_LANGUAGES)

    def add_translation(self, key: str, de: str = "", en: str = "", es: str = "", zh: str = "", ja: str = "", ru: str = "", **kwargs):
        """Fügt einen Übersetzungseintrag hinzu oder aktualisiert ihn."""
        entry = {
            "de": de or key,
            "en": en,
            "es": es,
            "zh": zh,
            "ja": ja,
            "ru": ru,
        }
        for k, v in kwargs.items():
            if k in SUPPORTED_LANGUAGES:
                entry[k] = v
        self.translations[key] = entry
        self._save_translations()

    def scan_and_update(self, project_dir: Optional[Path] = None) -> Dict:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            project_dir = self.app_dir

        found_strings = self._find_german_strings(project_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                self.translations[string] = {lang: (string if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
                added.append(string)

        if added:
            self._save_translations()

        missing = {
            lang: [k for k, v in self.translations.items() if not v.get(lang)]
            for lang in SUPPORTED_LANGUAGES if lang != "de"
        }

        return {
            'added': added,
            'missing': missing,
            'total': len(self.translations)
        }

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "äöüÄÖÜßaeoeueAeOeUess"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self, lang: str = "en") -> List[str]:
        """Liefert alle Keys, für die in der angegebenen Sprache keine Übersetzung existiert."""
        return [k for k, v in self.translations.items() if not v.get(lang)]


if __name__ == "__main__":
    tr = TranslationSystem('de')
    print(f"Aktive Sprache: {tr.get_language()}")
    print(f"Unterstützte Sprachen: {tr.get_supported_languages()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu")

