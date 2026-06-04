from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROFILE_FORMAT = "winstorepackager-project-v1"
SCHEMA_VERSION = 1


def split_capabilities(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(",")
    return [item.strip() for item in items if item and item.strip()]


def join_capabilities(values: list[str] | None) -> str:
    if not values:
        return ""
    return ", ".join(item.strip() for item in values if item and item.strip())


def validate_project_profile(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Projektprofil muss ein JSON-Objekt sein."]

    if data.get("format") != PROFILE_FORMAT:
        errors.append(f"Unbekanntes Format: {data.get('format')!r}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Nicht unterstützte Schema-Version: {data.get('schema_version')!r}")

    for key in ("metadata", "paths", "store", "documents", "settings"):
        if key not in data:
            errors.append(f"Abschnitt fehlt: {key}")
        elif not isinstance(data[key], dict):
            errors.append(f"Abschnitt {key} muss ein Objekt sein.")
    return errors


def detect_project_root(path_values: list[str]) -> Path | None:
    candidates: list[str] = []
    for raw_value in path_values:
        value = str(raw_value or "").strip()
        if not value:
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            continue
        base = path if path.is_dir() else path.parent
        candidates.append(str(base.resolve(strict=False)))

    if not candidates:
        return None
    try:
        return Path(os.path.commonpath(candidates))
    except ValueError:
        # Mixed-drive Windows paths have no common root; keep absolute paths instead.
        return None


def serialize_project_profile(state: dict[str, Any]) -> dict[str, Any]:
    project_root = detect_project_root(
        [
            state.get("script_path", ""),
            state.get("icon_path", ""),
            state.get("source_path", ""),
            state.get("installer_path", ""),
            state.get("output_dir", ""),
        ]
    )

    return {
        "format": PROFILE_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "project_root": str(project_root.as_posix()) if project_root else "",
        "metadata": {
            "app_name": _clean_text(state.get("app_name")),
            "publisher_display": _clean_text(state.get("publisher_display")),
            "identity_name": _clean_text(state.get("identity_name")),
            "version": _clean_text(state.get("version")),
        },
        "paths": {
            "script_path": _serialize_path(state.get("script_path"), project_root),
            "icon_path": _serialize_path(state.get("icon_path"), project_root),
            "source_path": _serialize_path(state.get("source_path"), project_root),
            "installer_path": _serialize_path(state.get("installer_path"), project_root),
            "output_dir": _serialize_path(state.get("output_dir"), project_root),
            "exe_name": _clean_text(state.get("exe_name")),
        },
        "store": {
            "privacy_url": _clean_text(state.get("privacy_url")),
            "support_url": _clean_text(state.get("support_url")),
            "capabilities": split_capabilities(state.get("capabilities")),
            "category": _clean_text(state.get("category")),
            "age_rating": _clean_text(state.get("age_rating")),
            "description": _clean_text(state.get("description")),
            "changelog": _clean_text(state.get("changelog")),
        },
        "documents": {
            "readme": _clean_text(state.get("readme")),
            "license_files": [
                _serialize_path(path_value, project_root)
                for path_value in state.get("license_files", [])
                if str(path_value or "").strip()
            ],
            "license_text_entries": [
                _clean_text(text_entry)
                for text_entry in state.get("license_text_entries", [])
                if _clean_text(text_entry)
            ],
        },
        "settings": {
            "enable_i18n": bool(state.get("enable_i18n", True)),
        },
    }


def deserialize_project_profile(
    data: dict[str, Any],
    *,
    profile_path: str | Path | None = None,
) -> dict[str, Any]:
    errors = validate_project_profile(data)
    if errors:
        raise ValueError("\n".join(errors))

    profile_dir = Path(profile_path).resolve(strict=False).parent if profile_path else None
    project_root = _resolve_project_root(str(data.get("project_root", "")).strip(), profile_dir)

    metadata = data.get("metadata", {})
    paths = data.get("paths", {})
    store = data.get("store", {})
    documents = data.get("documents", {})
    settings = data.get("settings", {})

    return {
        "app_name": _clean_text(metadata.get("app_name")),
        "publisher_display": _clean_text(metadata.get("publisher_display")),
        "identity_name": _clean_text(metadata.get("identity_name")),
        "version": _clean_text(metadata.get("version")),
        "script_path": _resolve_path(paths.get("script_path"), project_root, profile_dir),
        "icon_path": _resolve_path(paths.get("icon_path"), project_root, profile_dir),
        "source_path": _resolve_path(paths.get("source_path"), project_root, profile_dir),
        "installer_path": _resolve_path(paths.get("installer_path"), project_root, profile_dir),
        "output_dir": _resolve_path(paths.get("output_dir"), project_root, profile_dir),
        "exe_name": _clean_text(paths.get("exe_name")),
        "privacy_url": _clean_text(store.get("privacy_url")),
        "support_url": _clean_text(store.get("support_url")),
        "capabilities": join_capabilities(store.get("capabilities", [])),
        "category": _clean_text(store.get("category")),
        "age_rating": _clean_text(store.get("age_rating")),
        "description": _clean_text(store.get("description")),
        "changelog": _clean_text(store.get("changelog")),
        "readme": _clean_text(documents.get("readme")),
        "license_files": [
            _resolve_path(path_value, project_root, profile_dir)
            for path_value in documents.get("license_files", [])
            if str(path_value or "").strip()
        ],
        "license_text_entries": [
            _clean_text(text_entry)
            for text_entry in documents.get("license_text_entries", [])
            if _clean_text(text_entry)
        ],
        "enable_i18n": bool(settings.get("enable_i18n", True)),
    }


def write_project_profile(path: str | Path, state: dict[str, Any]) -> None:
    target = Path(path)
    data = serialize_project_profile(state)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_project_profile(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    data = json.loads(target.read_text(encoding="utf-8"))
    return deserialize_project_profile(data, profile_path=target)


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _serialize_path(raw_value: Any, project_root: Path | None) -> str:
    value = _clean_text(raw_value)
    if not value:
        return ""
    path = Path(value).expanduser()
    if project_root and path.is_absolute():
        try:
            return path.resolve(strict=False).relative_to(project_root.resolve(strict=False)).as_posix()
        except ValueError:
            return path.as_posix()
    return value.replace("\\", "/")


def _resolve_project_root(project_root: str, profile_dir: Path | None) -> Path | None:
    if not project_root:
        return profile_dir

    path = Path(project_root)
    if path.is_absolute():
        return path.resolve(strict=False)
    if profile_dir is None:
        return path
    return (profile_dir / path).resolve(strict=False)


def _resolve_path(raw_value: Any, project_root: Path | None, profile_dir: Path | None) -> str:
    value = _clean_text(raw_value)
    if not value:
        return ""

    path = Path(value)
    if path.is_absolute():
        return str(path)

    base_dir = project_root or profile_dir
    if base_dir is None:
        return value
    return str((base_dir / path).resolve(strict=False))
