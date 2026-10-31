"""
manage_translations.py - Auto-Scanner für GUI-Strings (DE, EN, ES, ZH, JA, RU)
================================================================================
Findet deutsche Strings in .py-Dateien und pflegt locales/translations.json.
Standardisiert gemäß P-006 / Tier-2-Mehrsprachigkeit.

Verwendung:
    python manage_translations.py [--check] [--dir PROJEKTVERZEICHNIS]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Set, Tuple

TRANSLATION_FILE = "locales/translations.json"
SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'\bt\(\s*["\']([^"\']+)["\']'),
    re.compile(r'\btr\(\s*["\']([^"\']+)["\']'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren", "wählen",
]


def _ensure_utf8_streams() -> None:
    """Rekonfiguriert sys.stdout und sys.stderr defensiv auf UTF-8 für Windows CLI."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass
    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass


_ensure_utf8_streams()


def is_german(text: str) -> bool:
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir: str) -> Set[str]:
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases', '.git', '.pytest_cache'}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file not in ("manage_translations.py", "translator.py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def check_translations(source_dir: str = ".") -> Tuple[bool, List[str], Dict[str, int]]:
    """
    Prüft Vollständigkeit und Wohlgeformtheit der Übersetzungen in locales/translations.json.
    Standardisiert gemäß P-006 Tier-2 (6 Sprachen: DE, EN, ES, ZH, JA, RU).
    """
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    errors: List[str] = []
    stats: Dict[str, int] = {lang: 0 for lang in SUPPORTED_LANGUAGES}
    stats["total"] = 0

    if not os.path.exists(trans_file):
        errors.append(f"Übersetzungsdatei {trans_file} nicht gefunden.")
        return False, errors, stats

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Übersetzungsdatei {trans_file} enthält ungültiges JSON: {e}")
        return False, errors, stats
    except OSError as e:
        errors.append(f"Übersetzungsdatei {trans_file} konnte nicht gelesen werden: {e}")
        return False, errors, stats

    if not isinstance(translations, dict):
        errors.append(f"Übersetzungsdatei {trans_file} enthält kein Dictionary an der Wurzel.")
        return False, errors, stats

    total_keys = len(translations)
    stats["total"] = total_keys

    for key, lang_map in translations.items():
        if not isinstance(lang_map, dict):
            errors.append(f"Schlüssel '{key}' hat kein Dictionary als Wert.")
            continue

        for lang in SUPPORTED_LANGUAGES:
            val = lang_map.get(lang)
            if not val or not isinstance(val, str) or not val.strip():
                errors.append(f"Schlüssel '{key}' fehlt für Sprache '{lang}' oder ist leer.")
            else:
                stats[lang] += 1

    is_ok = len(errors) == 0
    return is_ok, errors, stats


def manage_translations(source_dir: str = ".") -> None:
    _ensure_utf8_streams()
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
        except (json.JSONDecodeError, OSError):
            translations = {}
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {lang: (s if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
            added.append(s)

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    tmp_file = trans_file + f".tmp.{os.getpid()}"
    with open(tmp_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, trans_file)

    if added:
        print(f"[+] {len(added)} neue Einträge hinzugefügt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    print("\n[i] Übersetzungsstatus:")
    for lang in [lang_code for lang_code in SUPPORTED_LANGUAGES if lang_code != "de"]:
        missing = [k for k, v in translations.items() if not v.get(lang)]
        status = f"[!] {len(missing)} fehlende Übersetzungen" if missing else "[ok] Vollständig (0 fehlend)"
        print(f"  - {lang.upper()}: {status}")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")


def main(argv: List[str] | None = None) -> int:
    _ensure_utf8_streams()
    default_dir = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(
        description="Auto-Scanner und Validator für GUI-Translations (P-006 Tier-2)"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=default_dir,
        help=f"Projektverzeichnis (Default: {default_dir})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validiert Vollständigkeit aller 6 Sprachen und beendet bei Fehlern mit Code 1 (CI-Gate)",
    )

    args = parser.parse_args(argv)
    source_dir = os.path.abspath(args.dir)

    if args.check:
        is_ok, errors, stats = check_translations(source_dir)
        trans_file = os.path.join(source_dir, TRANSLATION_FILE)
        print(f"=== Translation Audit: WinStorePackager ({trans_file}) ===")
        print(f"Unterstützte Sprachen (P-006): {', '.join(SUPPORTED_LANGUAGES)}")
        total = stats.get("total", 0)
        print(f"Gefundene Schlüssel: {total}\n")

        print("Übersetzungsabdeckung:")
        for lang in SUPPORTED_LANGUAGES:
            count = stats.get(lang, 0)
            status = "[ok] 100% vollständig" if count == total and total > 0 else f"[!] {count}/{total} Einträge"
            print(f"  - [{lang.upper()}]: {status} ({count} Strings)")

        if errors:
            print(f"\n[!] Gefundene Fehler ({len(errors)}):")
            for err in errors[:20]:
                print(f"  - {err}")
            if len(errors) > 20:
                print(f"  ... und {len(errors) - 20} weitere")
            return 1

        print("\n[ok] Alle Übersetzungen sind vollständig, wohlgeformt und valide!")
        return 0

    manage_translations(source_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
