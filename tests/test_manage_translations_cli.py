"""Contract tests for manage_translations.py CLI & fail-closed catalog protection."""

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
    """Verify CLI flags and fail-closed handling of corrupt translations catalogs."""

    def test_cli_check_passes_and_creates_no_flag_dirs(self):
        proc = subprocess.run(
            [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", str(REPO_ROOT), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse((REPO_ROOT / "--check").exists())
        self.assertFalse((REPO_ROOT / "--dir").exists())

    def test_scan_never_empties_an_unreadable_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "locales").mkdir()
            (root / "sample.py").write_text('label = QLabel("Fehler beim Laden")\n', encoding="utf-8")
            corrupt = "<<<<<<< HEAD\n{\"ok\": {}}\n=======\n"
            trans = root / "locales" / "translations.json"
            trans.write_text(corrupt, encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", str(root)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("[FAIL]", proc.stdout)
            self.assertEqual(trans.read_text(encoding="utf-8"), corrupt)

    def test_scan_rejects_non_object_root_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "locales").mkdir()
            (root / "sample.py").write_text('label = QLabel("Fehler beim Laden")\n', encoding="utf-8")
            raw_list = json.dumps(["unexpected", "array"])
            trans = root / "locales" / "translations.json"
            trans.write_text(raw_list, encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", str(root)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("[FAIL]", proc.stdout)
            self.assertEqual(trans.read_text(encoding="utf-8"), raw_list)

    def test_scan_creates_missing_translations_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text('label = QLabel("Fehler beim Laden")\n', encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(MANAGE_TRANSLATIONS_PY), "--dir", str(root)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            # Scan adds the untranslated string (missing target languages -> exit 1 on --check/parity)
            trans = root / "locales" / "translations.json"
            self.assertTrue(trans.is_file())
            data = json.loads(trans.read_text(encoding="utf-8"))
            self.assertIn("Fehler beim Laden", data)
            self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
