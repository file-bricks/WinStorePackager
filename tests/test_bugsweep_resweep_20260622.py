# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Desktop-Re-Sweep 2026-06-22 (Bugsweep-Loop-Lauf 25).

generate_manifest ist (mit minimaler App) aufrufbar -> echter XML-Wohlgeformtheitstest;
subprocess-Timeouts + atomares Save -> statische Assertions. Red-on-revert: WSP_SRC -> PRE-Backup.

  M  generate_manifest: ALLE Felder XML-escapen (nicht nur APPNAME) -> kein kaputtes MSIX bei &/<.
  T1 build_and_sign_msix: makeappx/signtool subprocess.run mit timeout.
  T2 build_exe: PyInstaller-Timeout (Notbremse).
  T3 install_and_import: kein Runtime-pip.
  A  save_settings: atomar über den Runtime-Pfad-Helper.
"""
import os
import sys
import tempfile
import xml.dom.minidom as minidom
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_SRC = Path(os.environ.get("WSP_SRC", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WSP = (_SRC / "WindowsStorePublisher_3.py").read_text(encoding="utf-8")


def has(n):
    return n in WSP


# --- echter Test: generate_manifest erzeugt wohlgeformtes XML (OHNE Tk-Root) ---
class _V:
    """Minimaler tk.StringVar-Ersatz (vermeidet echtes tk.Tk() -> keine Tcl-Pollution für andere Tests)."""
    def __init__(self, val):
        self._v = val
    def get(self):
        return self._v


def test_manifest_xml_wellformed_with_special_chars():
    import WindowsStorePublisher_3 as w

    # __new__ ohne __init__ -> kein Tk-Root nötig; generate_manifest nutzt nur .get()-Aufrufe.
    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    app.app_name = _V("App")
    app.publisher = _V("CN=Acme & Co")
    app.publisher_display = _V('Acme <b> & "Co"')
    app.identity_name = _V("Id.App")
    app.version = _V("1.0.0.0")
    app.capabilities = _V("")

    class _Box:
        def get(self, a, b):
            return 'Beschreibung mit & < > "Zitat"'
    app.desc_box = _Box()

    d = tempfile.mkdtemp()
    app.generate_manifest(d, "My&App.exe")
    xmltext = (Path(d) / "AppxManifest.xml").read_text(encoding="utf-8")
    # rohes "& Co" (unescaped) darf NICHT vorkommen
    assert "Acme & Co" not in xmltext
    assert "&amp;" in xmltext
    # muss wohlgeformt parsebar sein (vor dem Fix: ParseError) — selbst-generierter, trusted Input
    minidom.parseString(xmltext)


# --- statische Assertions (red-on-revert) ---
def test_manifest_all_fields_escaped():
    # alle user-text-Felder via html.escape (nicht nur APPNAME)
    for marker in ["{{IDENTITY_NAME}}", "{{PUBLISHER}}", "{{PUBLISHER_DISPLAY}}", "{{DESCRIPTION}}", "{{EXECUTABLE}}"]:
        idx = WSP.find(f'.replace("{marker}"')
        assert idx > 0, f"{marker} replace nicht gefunden"
        assert "html.escape(" in WSP[idx: idx + 200], f"{marker} nicht escaped"


def test_msix_subprocess_timeouts():
    assert has("check=True, timeout=300") and has("check=True, timeout=120"), "msix makeappx/signtool-Timeout fehlt"


def test_pyinstaller_timeout():
    assert has("env=build_env, timeout=1800"), "PyInstaller-Timeout fehlt"


def test_runtime_bootstrap_never_installs_packages():
    assert '"pip", "install", package_name' not in WSP, "Runtime-Bootstrap darf kein pip starten"
    assert "from release_contract import RUNTIME_DEPENDENCIES, install_command" in WSP
    contract = (_SRC / "release_contract.py").read_text(encoding="utf-8")
    assert "python -m pip install -r requirements.txt" in contract, "Reproduzierbarer Setup-Hinweis fehlt"


def test_save_settings_atomic():
    assert has("write_json_atomic(SETTINGS_FILE, data)"), "save_settings atomar fehlt"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])


def test_manifest_declares_language_resources():
    """Ohne <Resources> loest der Store keine sprachabhaengigen Werte auf.

    Der Store meldete DisplayName, PublisherDisplayName und die Logos dann als
    leer bzw. "not found" - obwohl sie im Manifest standen (ProfiPrompt,
    2026-08-10).
    """
    import WindowsStorePublisher_3 as w

    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    app.app_name = _V("App")
    app.publisher = _V("CN=Acme")
    app.publisher_display = _V("Acme")
    app.identity_name = _V("Id.App")
    app.version = _V("1.0.0.0")
    app.capabilities = _V("")

    class _Box:
        def get(self, a, b):
            return "Beschreibung"
    app.desc_box = _Box()

    d = tempfile.mkdtemp()
    app.generate_manifest(d, "App.exe")
    xmltext = (Path(d) / "AppxManifest.xml").read_text(encoding="utf-8")

    assert "<Resources>" in xmltext
    assert 'Resource Language="en-us"' in xmltext
    minidom.parseString(xmltext)


def test_restricted_capabilities_use_rescap_namespace():
    """runFullTrust als schlichtes <Capability> laesst makeappx das ganze
    Manifest ablehnen ("verstoesst gegen enumeration-Einschraenkung")."""
    import WindowsStorePublisher_3 as w

    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    app.app_name = _V("App")
    app.publisher = _V("CN=Acme")
    app.publisher_display = _V("Acme")
    app.identity_name = _V("Id.App")
    app.version = _V("1.0.0.0")
    app.capabilities = _V("internetClient,runFullTrust")

    class _Box:
        def get(self, a, b):
            return "Beschreibung"
    app.desc_box = _Box()

    d = tempfile.mkdtemp()
    app.generate_manifest(d, "App.exe")
    xmltext = (Path(d) / "AppxManifest.xml").read_text(encoding="utf-8")

    # internetClient ist allgemein, runFullTrust eingeschraenkt
    assert '<Capability Name="internetClient"/>' in xmltext
    assert '<rescap:Capability Name="runFullTrust"/>' in xmltext
    minidom.parseString(xmltext)


def test_stage_payload_takes_whole_folder_for_onedir_builds(tmp_path):
    """Bei PyInstaller --onedir liegen Laufzeit und Bibliotheken neben der EXE.

    Kopiert man nur die EXE, laesst sich das MSIX installieren, die App startet
    aber nicht.
    """
    import WindowsStorePublisher_3 as w

    dist = tmp_path / "dist" / "App"
    (dist / "_internal").mkdir(parents=True)
    (dist / "App.exe").write_bytes(b"MZ")
    (dist / "_internal" / "python3.dll").write_bytes(b"dll")
    (dist / "_internal" / "base_library.zip").write_bytes(b"zip")

    outdir = tmp_path / "staging"
    outdir.mkdir()

    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    count = app.stage_payload(str(dist / "App.exe"), str(outdir))

    assert count == 3
    assert (outdir / "App.exe").exists()
    assert (outdir / "_internal" / "python3.dll").exists()
    assert (outdir / "_internal" / "base_library.zip").exists()


def test_stage_payload_copies_single_file_for_onefile_builds(tmp_path):
    """Ohne _internal daneben bleibt es bei der einzelnen Datei."""
    import WindowsStorePublisher_3 as w

    src = tmp_path / "App.exe"
    src.write_bytes(b"MZ")
    outdir = tmp_path / "staging"
    outdir.mkdir()

    app = w.StorePackagerApp.__new__(w.StorePackagerApp)
    count = app.stage_payload(str(src), str(outdir))

    assert count == 1
    assert (outdir / "App.exe").exists()
