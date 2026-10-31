"""
Vertragstests für manage_translations.py CLI-Interface, Argument-Parsing,
6-Sprachen-Paritätsprüfung (P-006 Tier-2) und UTF-8-Encoding-Resilienz.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANAGE_TRANSLATIONS_PY = REPO_ROOT / "manage_translations.py"


class TestManageTranslationsCli(unittest.TestCase):
    """Prüft das CLI-Verhalten und die Paritätsprüfung von manage_translations.py."""

    def test_cli_check_does_not_create_check_directory(self):
        """--check darf niemals als Ordnername interpretiert werden und keinen Ordner anlegen."""
        check_dir = REPO_ROOT / "--check"
        if check_dir.exists():
            import shutil
            shutil.rmtree(check_dir)

        proc = subprocess.run(
            [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        self.assertFalse(check_dir.exists(), "manage_translations.py hat einen Ordner '--check' angelegt!")
        self.assertEqual(proc.returncode, 0, f"manage_translations.py --check schlug fehl: {proc.stderr}")
        self.assertIn("Translation Audit", proc.stdout)
        self.assertIn("100% vollständig", proc.stdout)

    def test_cli_dir_argument_resolves_properly(self):
        """--dir <pfad> muss als Verzeichnisargument erkannt werden und nicht als Ordner '--dir'."""
        dir_dir = REPO_ROOT / "--dir"
        if dir_dir.exists():
            import shutil
            shutil.rmtree(dir_dir)

        proc = subprocess.run(
            [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", str(REPO_ROOT), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        self.assertFalse(dir_dir.exists(), "manage_translations.py hat einen Ordner '--dir' angelegt!")
        self.assertEqual(proc.returncode, 0, f"manage_translations.py --dir . --check schlug fehl: {proc.stderr}")

    def test_cli_check_returns_exit_code_1_on_missing_translations(self):
        """--check muss bei unvollständigen Übersetzungen mit Exit-Code 1 abbrechen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            locales_dir = Path(tmpdir) / "locales"
            locales_dir.mkdir(parents=True)
            bad_json = {
                "Datei": {
                    "de": "Datei",
                    "en": "File",
                    "es": "",  # Fehlend!
                    "zh": "文件",
                    "ja": "ファイル",
                    "ru": "Файл",
                }
            }
            (locales_dir / "translations.json").write_text(json.dumps(bad_json, ensure_ascii=False), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", tmpdir, "--check"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            self.assertEqual(proc.returncode, 1, "manage_translations.py --check muss bei Lücken mit Exit 1 fehlschlagen!")
            self.assertIn("fehlt", proc.stdout.lower())

    def test_check_translations_unit_function(self):
        """check_translations() muss auf dem aktuellen Stand des Repositories 100% grün sein."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("manage_translations", str(MANAGE_TRANSLATIONS_PY))
        mt_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mt_mod)

        self.assertTrue(hasattr(mt_mod, "check_translations"), "manage_translations.py muss check_translations() exportieren")
        is_ok, errors, stats = mt_mod.check_translations(str(REPO_ROOT))
        self.assertTrue(is_ok, f"check_translations() lieferte Fehler: {errors}")
        self.assertEqual(errors, [])
        self.assertGreater(stats.get("total", 0), 200)
        for lang in ("de", "en", "es", "zh", "ja", "ru"):
            self.assertEqual(stats.get(lang), stats.get("total"), f"Sprache {lang} hat Lücken in stats!")

    def test_manage_translations_update_mode_idempotent(self):
        """manage_translations() im Schreibmodus darf keine Phantom-Strings (z.B. aus translator.py) anhängen."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("manage_translations", str(MANAGE_TRANSLATIONS_PY))
        mt_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mt_mod)

        # Vor Ausführung prüfen
        is_ok_before, errors_before, stats_before = mt_mod.check_translations(str(REPO_ROOT))
        self.assertTrue(is_ok_before, f"Ausgangszustand hat Fehler: {errors_before}")

        # Update-Modus ausführen
        mt_mod.manage_translations(str(REPO_ROOT))

        # Nach Ausführung muss weiterhin 100% Parität herrschen
        is_ok_after, errors_after, stats_after = mt_mod.check_translations(str(REPO_ROOT))
        self.assertTrue(is_ok_after, f"manage_translations() hat ungültige/unvollständige Keys erzeugt: {errors_after}")
        self.assertEqual(stats_after.get("total"), stats_before.get("total"), "manage_translations() hat unerwünschte Phantom-Keys angehängt!")


if __name__ == "__main__":
    unittest.main()
