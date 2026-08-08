import json
import os
from pathlib import Path

from project_profile import (
    PROFILE_FORMAT,
    deserialize_project_profile,
    read_project_profile,
    serialize_project_profile,
    validate_project_profile,
    write_project_profile,
)


def test_serialize_profile_uses_relative_project_paths_and_excludes_sensitive_fields(tmp_path: Path):
    project_root = tmp_path / "DemoApp"
    state = {
        "app_name": "Demo App",
        "publisher": "CN=REAL-PUBLISHER",
        "publisher_display": "Demo Studio",
        "identity_name": "Demo.App",
        "version": "1.2.3.4",
        "script_path": str(project_root / "src" / "main.py"),
        "icon_path": str(project_root / "assets" / "icon.png"),
        "source_path": str(project_root / "dist" / "source.zip"),
        "installer_path": str(project_root / "dist" / "DemoApp.exe"),
        "output_dir": str(project_root / "releases" / "store"),
        "exe_name": "DemoApp.exe",
        "pfx_path": r"C:\Secrets\demo.pfx",
        "pfx_password": "super-secret",
        "makeappx_path": r"C:\SDK\makeappx.exe",
        "signtool_path": r"C:\SDK\signtool.exe",
        "privacy_url": "https://example.com/privacy",
        "support_url": "https://example.com/support",
        "capabilities": "internetClient, webcam",
        "category": "Developer Tools",
        "age_rating": "3+",
        "description": "Beschreibung",
        "changelog": "Version 1.2.3.4\n- Neu",
        "readme": "README",
        "license_files": [str(project_root / "LICENSE.txt")],
        "license_text_entries": ["MIT"],
        "enable_i18n": True,
    }

    profile = serialize_project_profile(state)

    assert profile["format"] == PROFILE_FORMAT
    assert profile["project_root"] == project_root.as_posix()
    assert profile["paths"]["script_path"] == "src/main.py"
    assert profile["paths"]["icon_path"] == "assets/icon.png"
    assert profile["documents"]["license_files"] == ["LICENSE.txt"]
    assert "publisher" not in profile["metadata"]
    assert "pfx_path" not in str(profile)
    assert "super-secret" not in str(profile)


def test_deserialize_profile_resolves_paths_against_profile_root(tmp_path: Path):
    project_dir = tmp_path / "MyApp"
    project_dir.mkdir()
    profile_path = project_dir / "winstorepackager-project-v1.json"

    profile = {
        "format": PROFILE_FORMAT,
        "schema_version": 1,
        "project_root": ".",
        "metadata": {
            "app_name": "Demo App",
            "publisher_display": "Demo Studio",
            "identity_name": "Demo.App",
            "version": "1.2.3.4",
        },
        "paths": {
            "script_path": "src/main.py",
            "icon_path": "assets/icon.png",
            "source_path": "",
            "installer_path": "",
            "output_dir": "releases/store",
            "exe_name": "DemoApp.exe",
        },
        "store": {
            "privacy_url": "https://example.com/privacy",
            "support_url": "https://example.com/support",
            "capabilities": ["internetClient", "webcam"],
            "category": "Developer Tools",
            "age_rating": "3+",
            "description": "Beschreibung",
            "changelog": "Version 1.2.3.4\n- Neu",
        },
        "documents": {
            "readme": "README",
            "license_files": ["LICENSE.txt"],
            "license_text_entries": ["MIT"],
        },
        "settings": {"enable_i18n": False},
    }

    result = deserialize_project_profile(profile, profile_path=profile_path)

    assert result["capabilities"] == "internetClient, webcam"
    assert result["script_path"] == str((project_dir / "src/main.py").resolve(strict=False))
    assert result["output_dir"] == str((project_dir / "releases/store").resolve(strict=False))
    assert result["enable_i18n"] is False


def test_validate_project_profile_rejects_unknown_format():
    errors = validate_project_profile({"format": "wrong", "schema_version": 99})
    assert errors


def test_serialize_profile_keeps_absolute_paths_when_drives_do_not_match():
    state = {
        "app_name": "Demo App",
        "script_path": r"C:\Projects\DemoApp\src\main.py",
        "icon_path": r"D:\Assets\icon.png",
        "output_dir": r"C:\Projects\DemoApp\releases\store",
    }

    profile = serialize_project_profile(state)

    assert profile["project_root"] == ""
    assert profile["paths"]["script_path"] == "C:/Projects/DemoApp/src/main.py"
    assert profile["paths"]["icon_path"] == "D:/Assets/icon.png"


def test_write_read_serialize_roundtrip_preserves_exchange_contract(tmp_path: Path):
    project_root = tmp_path / "DemoApp"
    state = {
        "app_name": "Demo App",
        "publisher_display": "Demo Studio",
        "identity_name": "Demo.App",
        "version": "1.2.3.4",
        "script_path": str(project_root / "src" / "main.py"),
        "icon_path": str(project_root / "assets" / "icon.png"),
        "source_path": str(project_root / "dist" / "source.zip"),
        "installer_path": str(project_root / "dist" / "DemoApp.exe"),
        "output_dir": str(project_root / "releases" / "store"),
        "exe_name": "DemoApp.exe",
        "privacy_url": "https://example.com/privacy",
        "support_url": "https://example.com/support",
        "capabilities": "internetClient, webcam",
        "category": "Developer Tools",
        "age_rating": "3+",
        "description": "Beschreibung",
        "changelog": "Version 1.2.3.4\n- Neu",
        "readme": "README",
        "license_files": [str(project_root / "LICENSE.txt")],
        "license_text_entries": ["MIT"],
        "enable_i18n": False,
    }
    profile_path = tmp_path / "winstorepackager-project-v1.json"

    write_project_profile(profile_path, state)
    raw_profile = json.loads(profile_path.read_text(encoding="utf-8"))

    assert serialize_project_profile(read_project_profile(profile_path)) == raw_profile


def test_deserialize_preserves_foreign_windows_drive_paths(tmp_path: Path):
    profile = {
        "format": PROFILE_FORMAT,
        "schema_version": 1,
        "project_root": "",
        "metadata": {},
        "paths": {
            "script_path": "C:/Projects/Demo/src/main.py",
            "icon_path": "D:/Assets/icon.png",
            "source_path": "",
            "installer_path": "",
            "output_dir": "",
            "exe_name": "Demo.exe",
        },
        "store": {},
        "documents": {"license_files": []},
        "settings": {},
    }

    result = deserialize_project_profile(profile, profile_path=tmp_path / "profile.json")

    assert result["script_path"].replace("\\", "/") == "C:/Projects/Demo/src/main.py"
    assert result["icon_path"].replace("\\", "/") == "D:/Assets/icon.png"


def test_deserialize_windows_project_root_is_portable_across_hosts(tmp_path: Path):
    profile = {
        "format": PROFILE_FORMAT,
        "schema_version": 1,
        "project_root": "C:/Projects/Demo",
        "metadata": {},
        "paths": {
            "script_path": "src/main.py",
            "icon_path": "",
            "source_path": "",
            "installer_path": "",
            "output_dir": "",
            "exe_name": "Demo.exe",
        },
        "store": {},
        "documents": {"license_files": []},
        "settings": {},
    }

    result = deserialize_project_profile(profile, profile_path=tmp_path / "profile.json")
    if os.name == "nt":
        expected = Path("C:/Projects/Demo/src/main.py")
    else:
        expected = (tmp_path / "src/main.py").resolve(strict=False)

    assert Path(result["script_path"]).as_posix() == expected.as_posix()
