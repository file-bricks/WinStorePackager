"""Host-local runtime paths and settings migration for WinStorePackager."""

from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Mapping

APP_DIR_NAME = "WinStorePackager"
LINUX_APP_DIR_NAME = "winstorepackager"
SETTINGS_FILENAME = "settings_store_packager.json"
LOG_FILENAME = "winstorepackager.log"
_LOGGING_LOCK = threading.RLock()


def _resolved_home(home: Path | str | None) -> Path:
    return Path(home).expanduser() if home is not None else Path.home()


def _environment_path(
    environ: Mapping[str, str],
    name: str,
    fallback: Path,
    *,
    absolute_only: bool = False,
) -> Path:
    value = environ.get(name)
    if not value:
        return fallback
    candidate = Path(value).expanduser()
    if absolute_only and not candidate.is_absolute():
        return fallback
    return candidate


def _runtime_override(environ: Mapping[str, str], name: str) -> Path | None:
    value = environ.get(name)
    if not value:
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise ValueError(f"{name} muss ein absoluter Pfad sein.")
    return candidate


def get_config_dir(
    *,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> Path:
    """Return the host-local directory for machine-specific settings."""
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home_path = _resolved_home(home)

    if override := _runtime_override(environ, "WINSTOREPACKAGER_DATA_DIR"):
        return override
    if platform.startswith("win"):
        base = _environment_path(
            environ,
            "LOCALAPPDATA",
            home_path / "AppData" / "Local",
        )
        return base / APP_DIR_NAME
    if platform == "darwin":
        return home_path / "Library" / "Application Support" / APP_DIR_NAME

    base = _environment_path(
        environ,
        "XDG_CONFIG_HOME",
        home_path / ".config",
        absolute_only=True,
    )
    return base / LINUX_APP_DIR_NAME


def get_log_dir(
    *,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | str | None = None,
) -> Path:
    """Return the host-local directory for runtime logs."""
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home_path = _resolved_home(home)

    if override := _runtime_override(environ, "WINSTOREPACKAGER_LOG_DIR"):
        return override
    if platform.startswith("win"):
        return get_config_dir(platform=platform, environ=environ, home=home_path) / "logs"
    if platform == "darwin":
        return home_path / "Library" / "Logs" / APP_DIR_NAME

    base = _environment_path(
        environ,
        "XDG_STATE_HOME",
        home_path / ".local" / "state",
        absolute_only=True,
    )
    return base / LINUX_APP_DIR_NAME / "logs"


def get_settings_path() -> Path:
    return get_config_dir() / SETTINGS_FILENAME


def get_log_path() -> Path:
    return get_log_dir() / LOG_FILENAME


def configure_runtime_logging(log_path: Path | str | None = None) -> logging.Logger:
    """Configure one rotating UTF-8 file handler for application diagnostics."""
    target = Path(log_path) if log_path is not None else get_log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LINUX_APP_DIR_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    with _LOGGING_LOCK:
        resolved_target = target.resolve()
        for handler in list(logger.handlers):
            if not getattr(handler, "_wsp_runtime_handler", False):
                continue
            if Path(handler.baseFilename).resolve() == resolved_target:
                return logger
            logger.removeHandler(handler)
            handler.close()

        handler = RotatingFileHandler(
            target,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler._wsp_runtime_handler = True
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        return logger


def _write_json_temporary(target: Path, data: Mapping[str, object]) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    return temporary


def write_json_atomic(path: Path | str, data: Mapping[str, object]) -> None:
    """Write a JSON object atomically and restrict access where supported."""
    target = Path(path)
    temporary = _write_json_temporary(target, data)
    try:
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_json_if_absent(path: Path | str, data: Mapping[str, object]) -> bool:
    """Atomically publish JSON only when the target does not already exist."""
    target = Path(path)
    temporary = _write_json_temporary(target, data)
    try:
        try:
            os.link(temporary, target)
        except FileExistsError:
            return False
        return True
    finally:
        if temporary.exists():
            temporary.unlink()


def migrate_legacy_settings(legacy_path: Path | str, target_path: Path | str) -> bool:
    """Move valid checkout-local settings to the host-local runtime directory.

    Existing runtime settings always win. Invalid legacy JSON is preserved and
    reported to the caller instead of being overwritten or deleted.
    """
    legacy = Path(legacy_path)
    target = Path(target_path)
    if target.exists() or not legacy.exists() or legacy.resolve() == target.resolve():
        return False

    try:
        data = json.loads(legacy.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Legacy-Einstellungen sind kein gültiges JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Legacy-Einstellungen müssen ein JSON-Objekt sein.")

    if not _write_json_if_absent(target, data):
        return False
    if json.loads(target.read_text(encoding="utf-8")) != data:
        raise OSError("Readback der migrierten Einstellungen ist fehlgeschlagen.")

    try:
        legacy.unlink()
    except OSError:
        return False
    return True
