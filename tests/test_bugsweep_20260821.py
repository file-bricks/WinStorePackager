# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Bugsweep-Iteration 2026-08-21.

Prüft:
1. DeviceCapability-Kategorisierung in AppxManifest.xml:
   Hardware-/Geraetefaehigkeiten wie webcam, microphone, location, bluetooth
   werden als <DeviceCapability Name="..."/> statt fälschlicherweise als <rescap:Capability> emittiert.
2. Identity Name Fallback-Sanitization:
   Wenn identity_name leer gelassen wird, wird der Fallback YourCompany.{AppId}
   ueber sanitize_application_id bereinigt (keine Leerzeichen/Sonderzeichen),
   sodass ST_PackageIdentityName stets schema-valide bleibt.
3. Publisher CN-Validierung:
   validate_publisher_cn weist None, Leerstrings und unvollständige "CN="-Präfixe ab.
4. project_profile Null-Safety & Robustheit:
   deserialize_project_profile verarbeitet JSON-Dokumente mit null/None-Feldern fuer
   license_files/license_text_entries ohne TypeError, und join_capabilities verarbeitet
   sowohl Listen als auch Strings und None.
"""
import sys
import tempfile
from pathlib import Path
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import WindowsStorePublisher_3 as wsp
from project_profile import (
    PROFILE_FORMAT,
    deserialize_project_profile,
    join_capabilities,
)


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


def _build_manifest(app_name="DemoApp", identity="", capabilities="", publisher="CN=TestStudio"):
    app = wsp.StorePackagerApp.__new__(wsp.StorePackagerApp)
    app.app_name = _V(app_name)
    app.publisher = _V(publisher)
    app.publisher_display = _V("Test Studio")
    app.identity_name = _V(identity)
    app.version = _V("1.0.0.0")
    app.capabilities = _V(capabilities)
    app.desc_box = _Box()
    tmp = tempfile.mkdtemp()
    app.generate_manifest(tmp, "App.exe")
    return (Path(tmp) / "AppxManifest.xml").read_text(encoding="utf-8")


def test_device_capabilities_manifest_emission():
    """Geraetefaehigkeiten (webcam, microphone, location, bluetooth) muessen <DeviceCapability> sein."""
    caps = "internetClient, documentsLibrary, webcam, microphone, location, bluetooth, runFullTrust"
    manifest_xml = _build_manifest(capabilities=caps)
    doc = minidom.parseString(manifest_xml)

    cap_nodes = doc.getElementsByTagName("Capability")
    uap_nodes = doc.getElementsByTagName("uap:Capability")
    device_nodes = doc.getElementsByTagName("DeviceCapability")
    rescap_nodes = doc.getElementsByTagName("rescap:Capability")

    cap_names = [n.getAttribute("Name") for n in cap_nodes]
    uap_names = [n.getAttribute("Name") for n in uap_nodes]
    device_names = [n.getAttribute("Name") for n in device_nodes]
    rescap_names = [n.getAttribute("Name") for n in rescap_nodes]

    assert "internetClient" in cap_names
    assert "documentsLibrary" in uap_names
    assert "webcam" in device_names
    assert "microphone" in device_names
    assert "location" in device_names
    assert "bluetooth" in device_names
    assert "runFullTrust" in rescap_names

    # webcam darf keinesfalls in rescap sein
    assert "webcam" not in rescap_names
    assert "microphone" not in rescap_names


def test_identity_name_fallback_is_sanitized():
    """Wenn identity_name leer ist, muss der Fallback schema-valide sein (keine Leerzeichen)."""
    manifest_xml = _build_manifest(app_name="SQLite Viewer Pro", identity="")
    doc = minidom.parseString(manifest_xml)
    identity_node = doc.getElementsByTagName("Identity")[0]
    name_attr = identity_node.getAttribute("Name")

    assert name_attr == "YourCompany.SQLiteViewerPro"
    assert " " not in name_attr


def test_validate_publisher_cn_robustness():
    """validate_publisher_cn prueft None, Leerstring und leere 'CN=' Werte."""
    ok, msg = wsp.validate_publisher_cn(None)
    assert not ok
    assert "leer" in msg.lower()

    ok, msg = wsp.validate_publisher_cn("")
    assert not ok
    assert "leer" in msg.lower()

    ok, msg = wsp.validate_publisher_cn("   ")
    assert not ok
    assert "leer" in msg.lower()

    ok, msg = wsp.validate_publisher_cn("CN=")
    assert not ok
    assert "nach 'cn='" in msg.lower()

    ok, msg = wsp.validate_publisher_cn("InvalidFormat")
    assert not ok
    assert "muss mit 'cn=' beginnen" in msg.lower()

    ok, msg = wsp.validate_publisher_cn("CN=MyPublisher, O=MyCompany")
    assert ok
    assert msg == ""


def test_project_profile_null_safety():
    """deserialize_project_profile darf bei null-Feldern nicht mit TypeError abstürzen."""
    profile_data = {
        "format": PROFILE_FORMAT,
        "schema_version": 1,
        "project_root": "",
        "metadata": {"app_name": "Test"},
        "paths": {"script_path": ""},
        "store": {"capabilities": None},
        "documents": {
            "license_files": None,
            "license_text_entries": None,
        },
        "settings": {},
    }

    state = deserialize_project_profile(profile_data)
    assert state["capabilities"] == ""
    assert state["license_files"] == []
    assert state["license_text_entries"] == []


def test_join_capabilities_with_str_and_none():
    """join_capabilities unterstuetzt String, Liste und None."""
    assert join_capabilities(None) == ""
    assert join_capabilities([]) == ""
    assert join_capabilities(["internetClient", "webcam"]) == "internetClient, webcam"
    assert join_capabilities("internetClient, webcam") == "internetClient, webcam"
