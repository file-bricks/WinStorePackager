import hashlib
import json
import re
import struct
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
WINDOWS_STORE = ROOT / "releases" / "windowsstore"


def _read_text(path: Path) -> str:
    if not path.exists():
        pytest.skip(f"local Store dogfood artifact is not present: {path}")
    return path.read_text(encoding="utf-8")


def _png_size(path: Path) -> tuple[int, int]:
    if not path.exists():
        pytest.skip(f"local Store screenshot is not present: {path}")
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.name} is not a PNG"
    return struct.unpack(">II", data[16:24])


def _short_description(markdown: str) -> str:
    marker = "## Short Description"
    if marker not in markdown:
        marker = "## Kurzbeschreibung"
    section = markdown.split(marker, 1)[1]
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return lines[0]


def test_dogfood_release_msix_hash_is_documented_in_wack_protocol():
    msix_path = ROOT / "releases" / "WinStorePackager.msix"
    if not msix_path.exists():
        pytest.skip("local MSIX artifact is not present")
    protocol = _read_text(WINDOWS_STORE / "WACK_PROTOCOL.md")
    digest = hashlib.sha256(msix_path.read_bytes()).hexdigest().upper()

    assert msix_path.is_file()
    assert digest in protocol
    assert "releases/WinStorePackager.msix" in protocol


def test_store_dogfood_docs_use_portable_paths():
    stale_fragments = [
        r"C:\Users\User",
        r"OneDrive\Software Entwicklung",
    ]
    checked_docs = [
        WINDOWS_STORE / "BUILD.md",
        WINDOWS_STORE / "WACK_PROTOCOL.md",
    ]

    for path in checked_docs:
        text = _read_text(path)
        for fragment in stale_fragments:
            assert fragment not in text, f"{path.name} still contains {fragment}"
        assert "<PROJECT_ROOT>" in text or "<SOFTWARE_ROOT>" in text


def test_store_listing_profile_and_settings_stay_in_sync():
    profile = json.loads((ROOT / "winstorepackager-project-v1.json").read_text(encoding="utf-8"))
    store_package = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    store_settings = json.loads((WINDOWS_STORE / "store_settings.json").read_text(encoding="utf-8"))
    listing_de = _read_text(WINDOWS_STORE / "store_listing_de.md")
    listing_en = _read_text(WINDOWS_STORE / "store_listing_en.md")

    assert profile["metadata"]["app_name"] == store_package["app_name"] == store_settings["app_name"]
    assert profile["metadata"]["version"] == store_package["version"] == store_settings["version"]
    assert profile["store"]["privacy_url"] == store_package["privacy_url"] == store_settings["privacy_url"]
    assert profile["store"]["support_url"] == store_package["support_url"] == store_settings["support_url"]

    for listing in (listing_de, listing_en):
        assert store_package["privacy_url"] in listing
        assert store_package["support_url"] in listing
        assert store_package["app_name"] in listing
        assert len(_short_description(listing)) <= 100
        assert not re.search(r"\b(TODO|FIXME)\b", listing)


def test_store_screenshot_set_is_complete_and_store_sized():
    screenshots = sorted((WINDOWS_STORE / "screenshots").glob("*.png"))

    assert [path.name for path in screenshots] == [
        "01-main-window.png",
        "02-store-fields.png",
        "03-icon-generation.png",
        "04-msix-wack-workflow.png",
    ]
    assert all(_png_size(path) == (1920, 1080) for path in screenshots)
