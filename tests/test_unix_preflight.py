import json
import warnings
from pathlib import Path

from linux_preflight import run_linux_preflight
from project_profile import write_project_profile
from unix_preflight import run_unix_preflight


def test_unix_preflight_accepts_valid_repo_and_profile(tmp_path: Path):
    root = _create_repo(tmp_path)
    profile_path = root / "winstorepackager-project-v1.json"
    write_project_profile(
        profile_path,
        {
            "app_name": "WinStorePackager",
            "publisher_display": "File Bricks",
            "identity_name": "FileBricks.WinStorePackager",
            "version": "2.3.0.0",
            "script_path": str(root / "WindowsStorePublisher_3.py"),
            "icon_path": str(root / "WinStorePackager.ico"),
            "output_dir": str(root / "store_package"),
            "exe_name": "WinStorePackager.exe",
            "privacy_url": "https://example.com/privacy",
            "support_url": "https://example.com/support",
            "capabilities": "internetClient, runFullTrust",
            "category": "Developer Tools",
            "age_rating": "3+",
            "description": "MSIX helper",
            "readme": "README",
            "license_files": [str(root / "LICENSE")],
            "license_text_entries": ["MIT"],
        },
    )

    report = run_unix_preflight(root, profile_path=profile_path)

    assert report["ok"] is True
    assert report["errors"] == []


def test_unix_preflight_reports_missing_artifacts_and_invalid_urls(tmp_path: Path):
    root = _create_repo(tmp_path)
    (root / "STORE_LISTING.md").unlink()
    (root / "README" / "screenshots" / "main.png").unlink()
    (root / "WinStorePackager.ico").unlink()
    (root / "WinstorePackager_icon.jpg").unlink()
    (root / "store_package.json").write_text(
        json.dumps(
            {
                "app_name": "WinStorePackager",
                "version": "2.3",
                "description": "",
                "executable": "WinStorePackager",
                "category": "",
                "age_rating": "",
                "privacy_url": "file://privacy",
                "support_url": "",
            }
        ),
        encoding="utf-8",
    )

    report = run_unix_preflight(root)

    assert report["ok"] is False
    assert any("Store-Listing fehlt" in item for item in report["errors"])
    assert any("Version hat falsches Format" in item for item in report["errors"])
    assert any("`executable` muss auf `.exe` enden" in item for item in report["errors"])
    assert any("`privacy_url` muss mit http:// oder https:// beginnen" in item for item in report["errors"])
    assert any("`support_url` fehlt" in item for item in report["errors"])
    assert any("Icon-/Screenshot-Artefakte fehlen vollständig" in item for item in report["warnings"])


def test_unix_preflight_reports_missing_executable_as_missing(tmp_path: Path):
    """Leeres `executable`-Feld muss als „fehlt" gemeldet werden, nicht als „muss auf .exe enden"."""
    root = _create_repo(tmp_path)
    (root / "store_package.json").write_text(
        json.dumps(
            {
                "app_name": "WinStorePackager",
                "version": "2.3.0.0",
                "description": "MSIX helper",
                "executable": "",
                "category": "Developer Tools",
                "age_rating": "3+",
                "privacy_url": "https://example.com/privacy",
                "support_url": "https://example.com/support",
            }
        ),
        encoding="utf-8",
    )

    report = run_unix_preflight(root)

    assert report["ok"] is False
    assert any("`executable` fehlt" in item for item in report["errors"]), (
        "Leeres executable muss als 'fehlt' gemeldet werden"
    )
    assert not any("`executable` muss auf `.exe` enden" in item for item in report["errors"]), (
        "Bei leerem executable darf NICHT 'muss auf .exe enden' erscheinen"
    )


def test_unix_preflight_reports_missing_profile_executable_as_missing(tmp_path: Path):
    """Leeres oder fehlendes `exe_name` im Profil muss als 'fehlt' gemeldet werden, nicht als 'muss auf .exe enden'."""
    root = _create_repo(tmp_path)
    profile_path = root / "winstorepackager-project-v1.json"
    write_project_profile(
        profile_path,
        {
            "app_name": "WinStorePackager",
            "publisher_display": "File Bricks",
            "identity_name": "FileBricks.WinStorePackager",
            "version": "2.3.0.0",
            "script_path": str(root / "WindowsStorePublisher_3.py"),
            "icon_path": str(root / "WinStorePackager.ico"),
            "output_dir": str(root / "store_package"),
            "exe_name": "",
            "privacy_url": "https://example.com/privacy",
            "support_url": "https://example.com/support",
            "capabilities": "internetClient",
            "category": "Developer Tools",
            "age_rating": "3+",
            "description": "MSIX helper",
            "readme": "README",
            "license_files": [str(root / "LICENSE")],
            "license_text_entries": ["MIT"],
        },
    )

    report = run_unix_preflight(root, profile_path=profile_path)

    assert report["ok"] is False
    assert any("Projektprofil: `exe_name` fehlt" in item for item in report["errors"]), (
        "Leeres exe_name im Profil muss als 'fehlt' gemeldet werden"
    )
    assert not any("Projektprofil: `exe_name` muss auf `.exe` enden" in item for item in report["errors"]), (
        "Bei leerem exe_name im Profil darf NICHT 'muss auf .exe enden' erscheinen"
    )


def test_unix_preflight_validates_profile_app_name_and_version(tmp_path: Path):
    """Fehlender app_name oder ungültige Version im Profil müssen als Fehler gemeldet werden."""
    root = _create_repo(tmp_path)
    profile_path = root / "winstorepackager-project-v1.json"
    write_project_profile(
        profile_path,
        {
            "app_name": "",
            "publisher_display": "File Bricks",
            "identity_name": "FileBricks.WinStorePackager",
            "version": "invalid-version",
            "script_path": str(root / "WindowsStorePublisher_3.py"),
            "icon_path": str(root / "WinStorePackager.ico"),
            "output_dir": str(root / "store_package"),
            "exe_name": "WinStorePackager.exe",
            "privacy_url": "https://example.com/privacy",
            "support_url": "https://example.com/support",
            "capabilities": "internetClient",
            "category": "Developer Tools",
            "age_rating": "3+",
            "description": "MSIX helper",
            "readme": "README",
            "license_files": [str(root / "LICENSE")],
            "license_text_entries": ["MIT"],
        },
    )

    report = run_unix_preflight(root, profile_path=profile_path)

    assert report["ok"] is False
    assert any("Projektprofil: `app_name` fehlt" in item for item in report["errors"])
    assert any("Projektprofil: Version hat falsches Format" in item for item in report["errors"])


def test_unix_preflight_reports_missing_store_package_version_as_missing(tmp_path: Path):
    """Leeres version-Feld in store_package.json muss als 'fehlt' gemeldet werden, nicht als falsches Format ''."""
    root = _create_repo(tmp_path)
    (root / "store_package.json").write_text(
        json.dumps(
            {
                "app_name": "WinStorePackager",
                "version": "",
                "description": "MSIX helper",
                "executable": "WinStorePackager.exe",
                "category": "Developer Tools",
                "age_rating": "3+",
                "privacy_url": "https://example.com/privacy",
                "support_url": "https://example.com/support",
            }
        ),
        encoding="utf-8",
    )

    report = run_unix_preflight(root)

    assert report["ok"] is False
    assert any("store_package.json: `version` fehlt" in item for item in report["errors"]), (
        "Leere Version muss als 'fehlt' gemeldet werden"
    )
    assert not any("store_package.json: Version hat falsches Format: ''" in item for item in report["errors"]), (
        "Bei leerer Version darf NICHT 'Version hat falsches Format: ' erscheinen"
    )


def test_unix_preflight_warns_on_profile_and_store_package_drift(tmp_path: Path):
    root = _create_repo(tmp_path)
    profile_path = root / "winstorepackager-project-v1.json"
    write_project_profile(
        profile_path,
        {
            "app_name": "WinStorePackager Preview",
            "publisher_display": "File Bricks",
            "identity_name": "FileBricks.WinStorePackager",
            "version": "2.3.1.0",
            "script_path": str(root / "WindowsStorePublisher_3.py"),
            "icon_path": str(root / "WinStorePackager.ico"),
            "output_dir": str(root / "store_package"),
            "exe_name": "WinStorePackager.exe",
            "privacy_url": "https://example.com/privacy-preview",
            "support_url": "https://example.com/support",
            "capabilities": "internetClient",
            "category": "Developer Tools",
            "age_rating": "3+",
            "description": "MSIX helper",
            "readme": "README",
            "license_files": [str(root / "LICENSE")],
            "license_text_entries": ["MIT"],
        },
    )

    report = run_unix_preflight(root, profile_path=profile_path)

    assert report["ok"] is True
    assert any("`app_name` stimmt nicht mit `store_package.json` überein" in item for item in report["warnings"])
    assert any("`version` stimmt nicht mit `store_package.json` überein" in item for item in report["warnings"])
    assert any("`privacy_url` weicht von `store_package.json` ab" in item for item in report["warnings"])


def test_linux_preflight_deprecated_wrapper(tmp_path: Path):
    root = _create_repo(tmp_path)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        report = run_linux_preflight(root)

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "run_linux_preflight is deprecated" in str(w[0].message)

    assert report["ok"] is True
    assert report["platform"] == "linux"


def _create_repo(tmp_path: Path) -> Path:
    root = tmp_path / "WinStorePackager"
    (root / "README" / "screenshots").mkdir(parents=True)
    (root / "store_package").mkdir()

    (root / "WindowsStorePublisher_3.py").write_text("print('ok')\n", encoding="utf-8")
    (root / "requirements.txt").write_text("Pillow\n", encoding="utf-8")
    (root / "README.md").write_text(
        "# WinStorePackager\n\nMicrosoft Store helper with local metadata.\n",
        encoding="utf-8",
    )
    (root / "PRIVACY_POLICY.md").write_text(
        "Alle Daten bleiben lokal auf dem Gerät.\n",
        encoding="utf-8",
    )
    (root / "STORE_LISTING.md").write_text(
        "Support: https://example.com/support\n",
        encoding="utf-8",
    )
    (root / "PROJECT_PROFILE_FORMAT.md").write_text(
        "winstorepackager-project-v1\n",
        encoding="utf-8",
    )
    (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (root / "WinStorePackager.ico").write_bytes(b"ico")
    (root / "WinstorePackager_icon.jpg").write_bytes(b"jpg")
    (root / "README" / "screenshots" / "main.png").write_bytes(b"png")
    (root / "store_package.json").write_text(
        json.dumps(
            {
                "app_name": "WinStorePackager",
                "version": "2.3.0.0",
                "description": "MSIX helper",
                "executable": "WinStorePackager.exe",
                "category": "Developer Tools",
                "age_rating": "3+",
                "privacy_url": "https://example.com/privacy",
                "support_url": "https://example.com/support",
            }
        ),
        encoding="utf-8",
    )

    return root
