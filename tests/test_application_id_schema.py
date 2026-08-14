"""Application/@Id muss dem AppX-Schema genuegen.

Belegt am 2026-08-14 beim Dogfooding gegen real eingereichte Store-Pakete:
Aus dem App-Namen "SQLite Viewer Pro" entstand die Id "SQLite Viewer ProApp".
ST_ApplicationId (ueber ST_AsciiWindowsId) erlaubt nur
([A-Za-z][A-Za-z0-9]*)(\\.[A-Za-z][A-Za-z0-9]*)* mit maximal 64 Zeichen -
Leerzeichen sind unzulaessig, makeappx weist ein solches Manifest ab.
Quelle: microsoft/msix-packaging, AppxManifestTypes.xsd.
"""
import re
import sys
import tempfile
from pathlib import Path
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import WindowsStorePublisher_3 as w  # noqa: E402

# ST_ApplicationId, eingeschraenkt auf ST_AsciiWindowsId + maxLength 64.
ST_APPLICATION_ID = re.compile(r"([A-Za-z][A-Za-z0-9]*)(\.[A-Za-z][A-Za-z0-9]*)*\Z")


class _V:
    def __init__(self, val):
        self._v = val

    def get(self):
        return self._v


class _Box:
    def __init__(self, text="Beschreibung"):
        self._t = text

    def get(self, a, b):
        return self._t


def _manifest_for(app_name, identity="Vendor.App", executable="App.exe"):
    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    app.app_name = _V(app_name)
    app.publisher = _V("CN=Test")
    app.publisher_display = _V("Test")
    app.identity_name = _V(identity)
    app.version = _V("1.0.0.0")
    app.capabilities = _V("runFullTrust")
    app.desc_box = _Box()
    d = tempfile.mkdtemp()
    app.generate_manifest(d, executable)
    return (Path(d) / "AppxManifest.xml").read_text(encoding="utf-8")


def _app_id(manifest_text):
    doc = minidom.parseString(manifest_text)
    return doc.getElementsByTagName("Application")[0].getAttribute("Id")


def test_application_id_is_schema_valid_for_names_with_spaces():
    app_id = _app_id(_manifest_for("SQLite Viewer Pro"))
    assert " " not in app_id
    assert ST_APPLICATION_ID.fullmatch(app_id), app_id


def test_application_id_is_schema_valid_for_awkward_names():
    for name in ["Clean-Markdown", "My_App 2", "7Zip Helper", "Ärger & Co", "   "]:
        app_id = _app_id(_manifest_for(name))
        assert ST_APPLICATION_ID.fullmatch(app_id), f"{name!r} -> {app_id!r}"
        assert len(app_id) <= 64


def test_application_id_matches_already_published_packages():
    """Neupacken darf die Id einer publizierten App nicht veraendern.

    Microsoft: "The app's identifier should not be changed after the app has
    been published to the Microsoft Store." Die drei real eingereichten
    Pakete nutzen den bereinigten Namen ohne Suffix.
    """
    for app_name, expected in [
        ("MethodenAnalyser", "MethodenAnalyser"),
        ("SQLite Viewer Pro", "SQLiteViewerPro"),
        ("PromptBoard", "PromptBoard"),
    ]:
        assert _app_id(_manifest_for(app_name)) == expected


def test_sanitize_application_id_unit():
    f = w.sanitize_application_id
    assert f("SQLite Viewer Pro") == "SQLiteViewerPro"
    assert f("Clean-Markdown") == "CleanMarkdown"
    assert f("Vendor.Sub App") == "Vendor.SubApp"
    assert f("7Zip") == "Zip"
    assert f("") == "App"
    assert f("---") == "App"
    assert len(f("A" * 200)) == 64
