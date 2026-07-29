# -*- coding: utf-8 -*-
"""Runtime-Pfad- und Legacy-Migrationsvertrag für WinStorePackager."""

import json
import os
import threading
from pathlib import Path

import pytest

from runtime_paths import (
    configure_runtime_logging,
    get_config_dir,
    get_log_dir,
    migrate_legacy_settings,
    write_json_atomic,
)


def test_windows_runtime_paths_use_local_app_data(tmp_path):
    local_app_data = tmp_path / "LocalAppData"
    env = {"LOCALAPPDATA": str(local_app_data)}

    assert get_config_dir(platform="win32", environ=env, home=tmp_path) == (
        local_app_data / "WinStorePackager"
    )
    assert get_log_dir(platform="win32", environ=env, home=tmp_path) == (
        local_app_data / "WinStorePackager" / "logs"
    )


def test_unix_runtime_paths_follow_platform_conventions(tmp_path):
    assert get_config_dir(platform="darwin", environ={}, home=tmp_path) == (
        tmp_path / "Library" / "Application Support" / "WinStorePackager"
    )
    assert get_log_dir(platform="darwin", environ={}, home=tmp_path) == (
        tmp_path / "Library" / "Logs" / "WinStorePackager"
    )

    linux_env = {
        "XDG_CONFIG_HOME": str(tmp_path / "xdg-config"),
        "XDG_STATE_HOME": str(tmp_path / "xdg-state"),
    }
    assert get_config_dir(platform="linux", environ=linux_env, home=tmp_path) == (
        tmp_path / "xdg-config" / "winstorepackager"
    )
    assert get_log_dir(platform="linux", environ=linux_env, home=tmp_path) == (
        tmp_path / "xdg-state" / "winstorepackager" / "logs"
    )


def test_explicit_runtime_overrides_are_supported(tmp_path):
    env = {
        "WINSTOREPACKAGER_DATA_DIR": str(tmp_path / "config"),
        "WINSTOREPACKAGER_LOG_DIR": str(tmp_path / "logs"),
    }

    assert get_config_dir(platform="win32", environ=env, home=tmp_path) == tmp_path / "config"
    assert get_log_dir(platform="win32", environ=env, home=tmp_path) == tmp_path / "logs"


def test_empty_platform_environment_values_fall_back_to_home(tmp_path):
    env = {"LOCALAPPDATA": "", "XDG_CONFIG_HOME": "", "XDG_STATE_HOME": ""}

    assert get_config_dir(platform="win32", environ=env, home=tmp_path) == (
        tmp_path / "AppData" / "Local" / "WinStorePackager"
    )
    assert get_config_dir(platform="linux", environ=env, home=tmp_path) == (
        tmp_path / ".config" / "winstorepackager"
    )
    assert get_log_dir(platform="linux", environ=env, home=tmp_path) == (
        tmp_path / ".local" / "state" / "winstorepackager" / "logs"
    )


def test_relative_xdg_values_are_ignored_and_relative_overrides_are_rejected(tmp_path):
    xdg_env = {"XDG_CONFIG_HOME": "relative-config", "XDG_STATE_HOME": "relative-state"}
    assert get_config_dir(platform="linux", environ=xdg_env, home=tmp_path) == (
        tmp_path / ".config" / "winstorepackager"
    )
    assert get_log_dir(platform="linux", environ=xdg_env, home=tmp_path) == (
        tmp_path / ".local" / "state" / "winstorepackager" / "logs"
    )

    with pytest.raises(ValueError, match="absoluter Pfad"):
        get_config_dir(
            platform="win32",
            environ={"WINSTOREPACKAGER_DATA_DIR": "relative"},
            home=tmp_path,
        )
    with pytest.raises(ValueError, match="absoluter Pfad"):
        get_log_dir(
            platform="win32",
            environ={"WINSTOREPACKAGER_LOG_DIR": "relative"},
            home=tmp_path,
        )


def test_legacy_settings_are_migrated_without_overwriting_target(tmp_path):
    legacy = tmp_path / "checkout" / "settings_store_packager.json"
    target = tmp_path / "runtime" / "settings_store_packager.json"
    legacy.parent.mkdir()
    legacy.write_text(
        json.dumps({"publisher": "CN=Example", "pfx_path": "C:/private/signing.pfx"}),
        encoding="utf-8",
    )

    assert migrate_legacy_settings(legacy, target) is True
    assert not legacy.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {
        "publisher": "CN=Example",
        "pfx_path": "C:/private/signing.pfx",
    }

    legacy.write_text(json.dumps({"publisher": "CN=New"}), encoding="utf-8")
    assert migrate_legacy_settings(legacy, target) is False
    assert legacy.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["publisher"] == "CN=Example"


def test_invalid_legacy_settings_are_preserved(tmp_path):
    legacy = tmp_path / "settings_store_packager.json"
    target = tmp_path / "runtime" / "settings_store_packager.json"
    legacy.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON"):
        migrate_legacy_settings(legacy, target)

    assert legacy.exists()
    assert not target.exists()


def test_migration_race_does_not_overwrite_new_runtime_settings(tmp_path, monkeypatch):
    legacy = tmp_path / "checkout" / "settings_store_packager.json"
    target = tmp_path / "runtime" / "settings_store_packager.json"
    legacy.parent.mkdir()
    legacy.write_text(json.dumps({"publisher": "CN=Legacy"}), encoding="utf-8")

    real_link = os.link

    def publish_competing_settings(source, destination):
        target.write_text(json.dumps({"publisher": "CN=Current"}), encoding="utf-8")
        raise FileExistsError(destination)

    monkeypatch.setattr(os, "link", publish_competing_settings)
    try:
        assert migrate_legacy_settings(legacy, target) is False
    finally:
        monkeypatch.setattr(os, "link", real_link)

    assert legacy.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["publisher"] == "CN=Current"


def test_migration_preserves_legacy_when_cleanup_is_denied(tmp_path, monkeypatch):
    legacy = tmp_path / "checkout" / "settings_store_packager.json"
    target = tmp_path / "runtime" / "settings_store_packager.json"
    legacy.parent.mkdir()
    legacy.write_text(json.dumps({"publisher": "CN=Legacy"}), encoding="utf-8")
    real_unlink = Path.unlink

    def deny_legacy_cleanup(path, *args, **kwargs):
        if path == legacy:
            raise PermissionError("simulated cloud lock")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", deny_legacy_cleanup)

    assert migrate_legacy_settings(legacy, target) is False
    assert legacy.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["publisher"] == "CN=Legacy"


def test_atomic_json_write_creates_parent_and_leaves_no_temp_file(tmp_path):
    target = tmp_path / "runtime" / "settings.json"

    write_json_atomic(target, {"language": "de"})

    assert json.loads(target.read_text(encoding="utf-8")) == {"language": "de"}
    assert not list(target.parent.glob(f".{target.name}.*.tmp"))


def test_atomic_json_write_preserves_old_target_when_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / "runtime" / "settings.json"
    target.parent.mkdir()
    target.write_text(json.dumps({"language": "de"}), encoding="utf-8")

    def fail_replace(source, destination):
        raise PermissionError("simulated write lock")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(PermissionError, match="write lock"):
        write_json_atomic(target, {"language": "en"})

    assert json.loads(target.read_text(encoding="utf-8")) == {"language": "de"}
    assert not list(target.parent.glob(f".{target.name}.*.tmp"))


def test_runtime_logging_is_utf8_rotating_and_idempotent(tmp_path):
    log_path = tmp_path / "logs" / "winstorepackager.log"
    logger = configure_runtime_logging(log_path)
    try:
        same_logger = configure_runtime_logging(log_path)
        same_logger.info("Runtime-Pfad mit Umlaut: geprüft")
        for handler in logger.handlers:
            handler.flush()

        matching_handlers = [
            handler
            for handler in logger.handlers
            if Path(getattr(handler, "baseFilename", "")).resolve() == log_path.resolve()
        ]
        assert len(matching_handlers) == 1
        assert "geprüft" in log_path.read_text(encoding="utf-8")
    finally:
        for handler in list(logger.handlers):
            if Path(getattr(handler, "baseFilename", "")).resolve() == log_path.resolve():
                logger.removeHandler(handler)
                handler.close()


def test_runtime_logging_replaces_old_target_and_is_thread_safe(tmp_path):
    first_path = tmp_path / "first" / "winstorepackager.log"
    second_path = tmp_path / "second" / "winstorepackager.log"
    logger = configure_runtime_logging(first_path)
    try:
        threads = [
            threading.Thread(target=configure_runtime_logging, args=(second_path,))
            for _ in range(8)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        runtime_handlers = [
            handler
            for handler in logger.handlers
            if getattr(handler, "_wsp_runtime_handler", False)
        ]
        assert len(runtime_handlers) == 1
        assert Path(runtime_handlers[0].baseFilename).resolve() == second_path.resolve()

        logger.info("nur neues Ziel")
        runtime_handlers[0].flush()
        assert "nur neues Ziel" in second_path.read_text(encoding="utf-8")
        assert "nur neues Ziel" not in first_path.read_text(encoding="utf-8")
    finally:
        for handler in list(logger.handlers):
            if getattr(handler, "_wsp_runtime_handler", False):
                logger.removeHandler(handler)
                handler.close()
