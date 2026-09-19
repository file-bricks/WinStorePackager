# -*- coding: utf-8 -*-
"""Tests for Windows SDK tool detection in WindowsStorePublisher_3.py."""

import WindowsStorePublisher_3 as wsp


def test_find_windows_sdk_tools_scans_windows_kits_when_not_in_path(tmp_path, monkeypatch):
    # Simulate tools NOT in PATH
    monkeypatch.setattr(wsp, "which", lambda prog: None)

    # Create fake Windows Kits structure
    sdk_root = tmp_path / "Windows Kits" / "10"
    bin_dir = sdk_root / "bin" / "10.0.22621.0" / "x64"
    bin_dir.mkdir(parents=True)
    fake_makeappx = bin_dir / "makeappx.exe"
    fake_signtool = bin_dir / "signtool.exe"
    fake_makeappx.touch()
    fake_signtool.touch()

    appcert_dir = sdk_root / "App Certification Kit"
    appcert_dir.mkdir(parents=True)
    fake_appcert = appcert_dir / "appcert.exe"
    fake_appcert.touch()

    makeappx, signtool, appcert = wsp.find_windows_sdk_tools(search_roots=[sdk_root])

    assert makeappx == str(fake_makeappx)
    assert signtool == str(fake_signtool)
    assert appcert == str(fake_appcert)


def test_find_windows_sdk_tools_returns_partial_discoveries(tmp_path, monkeypatch):
    # Only makeappx is available via which()
    def mock_which(prog):
        if prog == "makeappx.exe":
            return r"C:\Custom\makeappx.exe"
        return None

    monkeypatch.setattr(wsp, "which", mock_which)

    makeappx, signtool, appcert = wsp.find_windows_sdk_tools(search_roots=[tmp_path])
    assert makeappx == r"C:\Custom\makeappx.exe"
    assert signtool is None
    assert appcert is None
