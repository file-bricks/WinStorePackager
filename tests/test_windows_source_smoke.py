"""
Windows-Source-Smoke Tests fuer WinStorePackager:

Prueft den Quellcode-Start, Repo-Preflight, Store-Paket-Metadaten
und WACK-Protokoll-Vollstaendigkeit unter Windows/CI.
"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from unix_preflight import run_unix_preflight


def test_windows_source_preflight_valid_repo():
    """Prueft, dass das bestehende WinStorePackager-Repo den Preflight fehlerfrei besteht."""
    root = Path(__file__).parent.parent
    report = run_unix_preflight(root)
    assert report["ok"] is True, f"Preflight-Fehler: {report['errors']}"
    assert len(report["errors"]) == 0


def test_windows_source_dogfood_readiness():
    """Prueft die Vollstaendigkeit von store_package.json im Repo."""
    root = Path(__file__).parent.parent
    store_package_file = root / "store_package.json"
    assert store_package_file.exists(), "store_package.json fehlt"

    data = json.loads(store_package_file.read_text(encoding="utf-8"))
    assert data.get("app_name") == "WinStorePackager"
    assert data.get("executable") == "WinStorePackager.exe"
    assert "privacy_url" in data and data["privacy_url"].startswith("http")
    assert "support_url" in data and data["support_url"].startswith("http")


def test_public_docs_do_not_reference_removed_web_companion():
    """Verhindert falsche Startanweisungen fuer den entfernten lokalen Web-Helfer."""
    root = Path(__file__).parent.parent
    for name in ("README.md", "README_de.md", "llms.txt"):
        content = (root / name).read_text(encoding="utf-8")
        assert "web_companion/" not in content, f"{name} verweist auf den entfernten Web-Helfer"


def test_windows_source_wack_protocol_present():
    """Prueft ein vorhandenes lokales WACK-Pruefprotokoll."""
    root = Path(__file__).parent.parent
    wack_protocol = root / "releases" / "windowsstore" / "WACK_PROTOCOL.md"
    if not wack_protocol.exists():
        pytest.skip("lokales WACK-Pruefprotokoll ist absichtlich nicht im Git-Repo")
    content = wack_protocol.read_text(encoding="utf-8")
    assert "WACK" in content
    assert "Windows App Certification Kit" in content or "appcert" in content


def test_windows_source_import_wsp_module():
    """Prueft, dass WindowsStorePublisher_3 importierbar ist ohne Nebenwirkungen."""
    import WindowsStorePublisher_3 as wsp

    root = Path(__file__).parent.parent.resolve()
    assert hasattr(wsp, "StorePackagerApp")
    assert hasattr(wsp, "install_and_import")
    assert not Path(wsp.SETTINGS_FILE).resolve().is_relative_to(root)
    assert not Path(wsp.LOG_FILE).resolve().is_relative_to(root)
    assert wsp.LEGACY_SETTINGS_FILE.resolve() == root / "settings_store_packager.json"
