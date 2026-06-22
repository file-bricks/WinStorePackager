# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Desktop-Re-Sweep 2026-06-22 (Bugsweep-Loop-Lauf 25).

generate_manifest ist (mit minimaler App) aufrufbar -> echter XML-Wohlgeformtheitstest;
subprocess-Timeouts + atomares Save -> statische Assertions. Red-on-revert: WSP_SRC -> PRE-Backup.

  M  generate_manifest: ALLE Felder XML-escapen (nicht nur APPNAME) -> kein kaputtes MSIX bei &/<.
  T1 build_and_sign_msix: makeappx/signtool subprocess.run mit timeout.
  T2 build_exe: PyInstaller-Timeout (Notbremse).
  T3 install_and_import: pip-Timeout.
  A  save_settings: atomar (tmp + os.replace).
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


def test_pip_timeout():
    assert has('"pip", "install", package_name], timeout=300'), "pip-Timeout fehlt"


def test_save_settings_atomic():
    assert has('tmp = f"{SETTINGS_FILE}.tmp"') and has("os.replace(tmp, SETTINGS_FILE)"), "save_settings atomar fehlt"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
