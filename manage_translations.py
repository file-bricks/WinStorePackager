"""
manage_translations.py - Multi-Language Translation Manager & CI Gate
======================================================================
Policy P-006: Tier-2 Multi-Language Standard (DE, EN, ES, ZH, JA, RU)

Verwendung:
    python manage_translations.py [--check] [--dir PROJEKTVERZEICHNIS] [--stats]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
TRANSLATION_FILE = "locales/translations.json"
SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'_t\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren", "wählen",
    "prüfen", "ordner", "ausgabe", "hinweis", "beenden",
]


def _ensure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError, AttributeError):
                pass


def is_german(text: str) -> bool:
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir: str | Path):
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases', '.git'}

    for root, dirs, files in os.walk(str(source_dir)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
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


def manage_translations(source_dir=".", check_only: bool = False, scan: bool = True) -> bool:
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

    if scan and not check_only:
        found = find_german_strings(source_dir)
        added = []
        for s in sorted(found):
            if s not in translations:
                translations[s] = {lang: (s if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
                added.append(s)

        if added:
            os.makedirs(os.path.dirname(trans_file), exist_ok=True)
            with open(trans_file, "w", encoding="utf-8") as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            print(f"[+] {len(added)} neue Einträge hinzugefügt:")
            for s in added[:20]:
                print(f"    - {s}")
            if len(added) > 20:
                print(f"    ... und {len(added) - 20} weitere")
        else:
            print("[i] Keine neuen deutschen Strings gefunden.")

    print("\n[i] Übersetzungsstatus:")
    all_ok = True
    for lang in [lang_code for lang_code in SUPPORTED_LANGUAGES if lang_code != "de"]:
        missing = [k for k, v in translations.items() if not v.get(lang)]
        status = f"[!] {len(missing)} fehlende Übersetzungen" if missing else "[ok] Vollständig (0 fehlend)"
        if missing:
            all_ok = False
        print(f"  - {lang.upper()}: {status}")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")
    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Language Translation Manager (P-006 / Tier-2)")
    parser.add_argument("--dir", default=str(APP_DIR), help="Projektverzeichnis")
    parser.add_argument("--check", action="store_true", help="CI-Gate: Validiert Parität ohne Modifikation")
    parser.add_argument("--scan", action="store_true", default=True, help="Quellcode scannen")
    parser.add_argument("--stats", action="store_true", help="Detaillierte Statistiken anzeigen")

    args, unknown = parser.parse_known_args()
    target_dir = args.dir
    if unknown and not unknown[0].startswith("-"):
        target_dir = unknown[0]

    ok = manage_translations(target_dir, check_only=args.check, scan=not args.check)
    if args.check and not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
