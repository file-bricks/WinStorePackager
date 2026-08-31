from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

PROFILE_FORMAT = "winstorepackager-project-v1"
SCHEMA_VERSION = 1
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_PROFILE_FIELDS = {
    "format",
    "schema_version",
    "project_root",
    "metadata",
    "paths",
    "store",
    "documents",
    "settings",
}
_SECTION_FIELDS = {
    "metadata": {"app_name", "publisher_display", "identity_name", "version"},
    "paths": {
        "script_path",
        "icon_path",
        "source_path",
        "installer_path",
        "output_dir",
        "exe_name",
    },
    "store": {
        "privacy_url",
        "support_url",
        "capabilities",
        "category",
        "age_rating",
        "description",
        "changelog",
    },
    "documents": {"readme", "license_files", "license_text_entries"},
    "settings": {"enable_i18n"},
}
_TEXT_FIELDS = {
    "metadata": _SECTION_FIELDS["metadata"],
    "paths": _SECTION_FIELDS["paths"],
    "store": _SECTION_FIELDS["store"] - {"capabilities"},
    "documents": {"readme"},
}
_LIST_FIELDS = {
    "store": {"capabilities"},
    "documents": {"license_files", "license_text_entries"},
}
_BOOL_FIELDS = {"settings": {"enable_i18n"}}
_PUBLISHER_ID_RE = re.compile(r"(?i)(?:^|[\s,;+])CN\s*=")
_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
    r"|-----BEGIN PGP PRIVATE KEY BLOCK-----",
    re.IGNORECASE,
)
_TOKEN_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)
_CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?i)(?P<quote>[\"']?)\b(?P<name>pfx[_-]?password|password|passwd|access[_-]?token|"
    r"auth[_-]?token|api[_-]?key|secret)(?P=quote)\s*[:=]\s*"
    r"(?P<value>[\"'][^\"']*[\"']|[^\s,;]+)"
)
_PLACEHOLDER_VALUE_RE = re.compile(
    r"(?i)^(?:"
    r"your[-_](?:api[-_]?key|key|token|secret|password)(?:[-_]here)?|"
    r"(?:example|sample|dummy|placeholder)(?:[-_](?:value|api[-_]?key|key|token|secret|password))?|"
    r"redacted|change[-_]?me|replace[-_]?me|required|none|null|n/?a"
    r")$"
)
_ENV_PLACEHOLDER_RE = re.compile(
    r"^(?:\$\{[A-Za-z_][A-Za-z0-9_]*\}|\$[A-Za-z_][A-Za-z0-9_]*|"
    r"%[A-Za-z_][A-Za-z0-9_]*%|\$env:[A-Za-z_][A-Za-z0-9_]*)$",
    re.IGNORECASE,
)
_BRACKETED_PLACEHOLDER_RE = re.compile(
    r"(?i)^(?:your[-_])?(?:api[-_]?key|key|token|secret|password|pfx[-_]?password)"
    r"(?:[-_]here)?$"
)
_WINDOWS_SDK_TOOLS = {"makeappx.exe", "signtool.exe", "appcert.exe"}
_CERTIFICATE_SUFFIXES = {".pfx", ".p12"}


def split_capabilities(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(",")
    return [item.strip() for item in items if item and item.strip()]


def join_capabilities(values: list[str] | str | None) -> str:
    if not values:
        return ""
    if isinstance(values, str):
        values = split_capabilities(values)
    return ", ".join(item.strip() for item in values if item and item.strip())


def validate_project_profile(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Projektprofil muss ein JSON-Objekt sein."]

    if data.get("format") != PROFILE_FORMAT:
        errors.append(f"Unbekanntes Format: {data.get('format')!r}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Nicht unterstützte Schema-Version: {data.get('schema_version')!r}")

    for key in sorted(set(data) - _PROFILE_FIELDS):
        errors.append(f"Unbekanntes Feld: {key}")

    for key in ("metadata", "paths", "store", "documents", "settings"):
        if key not in data:
            errors.append(f"Abschnitt fehlt: {key}")
        elif not isinstance(data[key], dict):
            errors.append(f"Abschnitt {key} muss ein Objekt sein.")
        else:
            for field in sorted(set(data[key]) - _SECTION_FIELDS[key]):
                errors.append(f"Unbekanntes Feld: {key}.{field}")
            errors.extend(_validate_section_types(key, data[key]))

    project_root = data.get("project_root")
    if project_root is not None and not isinstance(project_root, str):
        errors.append("Feld project_root muss Text sein.")
    elif isinstance(project_root, str):
        errors.extend(_sensitive_path_errors("project_root", project_root))

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        for field, value in metadata.items():
            if isinstance(value, str) and _PUBLISHER_ID_RE.search(value):
                errors.append(
                    f"Sensibler Wert in metadata.{field}: Publisher-ID gehört nicht ins Austauschprofil."
                )

    paths = data.get("paths")
    if isinstance(paths, dict):
        for field, value in paths.items():
            if not isinstance(value, str):
                continue
            errors.extend(_sensitive_path_errors(f"paths.{field}", value))

    documents = data.get("documents")
    if isinstance(documents, dict):
        license_files = documents.get("license_files")
        if isinstance(license_files, list):
            for index, value in enumerate(license_files):
                if isinstance(value, str):
                    errors.extend(
                        _sensitive_path_errors(f"documents.license_files[{index}]", value)
                    )

    for field_path, value in _iter_string_values(data):
        if (
            _PRIVATE_KEY_RE.search(value)
            or _contains_non_placeholder_credential(value)
            or any(pattern.search(value) for pattern in _TOKEN_PATTERNS)
        ):
            errors.append(
                f"Sensibler Wert in {field_path}: Credential oder privater Schlüssel gehört nicht ins Austauschprofil."
            )
    return errors


def _validate_section_types(section: str, values: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field, value in values.items():
        if value is None or field not in _SECTION_FIELDS[section]:
            continue
        field_path = f"{section}.{field}"
        if field in _TEXT_FIELDS.get(section, set()) and not isinstance(value, str):
            errors.append(f"Feld {field_path} muss Text sein.")
        elif field in _LIST_FIELDS.get(section, set()):
            if not isinstance(value, list):
                errors.append(f"Feld {field_path} muss eine Textliste sein.")
            elif any(not isinstance(item, str) for item in value):
                errors.append(f"Feld {field_path} darf nur Texte enthalten.")
        elif field in _BOOL_FIELDS.get(section, set()) and not isinstance(value, bool):
            errors.append(f"Feld {field_path} muss ein Boolean sein.")
    return errors


def _iter_string_values(value: Any, field_path: str = "profile"):
    if isinstance(value, str):
        yield field_path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_string_values(item, f"{field_path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_string_values(item, f"{field_path}[{index}]")


def _path_basename(value: str) -> str:
    clean_value = re.split(r"[?#]", value, maxsplit=1)[0].replace("\\", "/")
    return clean_value.rsplit("/", 1)[-1].lower()


def _path_suffix(value: str) -> str:
    return Path(re.split(r"[?#]", value, maxsplit=1)[0]).suffix.lower()


def _sensitive_path_errors(field_path: str, value: str) -> list[str]:
    errors: list[str] = []
    if _path_basename(value) in _WINDOWS_SDK_TOOLS:
        errors.append(
            f"Sensibler Wert in {field_path}: Windows-SDK-Pfad gehört nicht ins Austauschprofil."
        )
    if _path_suffix(value) in _CERTIFICATE_SUFFIXES:
        errors.append(
            f"Sensibler Wert in {field_path}: Zertifikatsdatei gehört nicht ins Austauschprofil."
        )
    return errors


def _contains_non_placeholder_credential(value: str) -> bool:
    for match in _CREDENTIAL_ASSIGNMENT_RE.finditer(value):
        name = match.group("name").lower().replace("-", "_")
        secret_value = match.group("value").strip("\"'").strip()
        if not secret_value:
            continue
        if name == "pfx_password":
            return True
        if not _is_placeholder_value(secret_value):
            return True
    return False


def _is_placeholder_value(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized.startswith(("<", "{", "[")) and normalized.endswith((">", "}", "]")):
        return bool(_BRACKETED_PLACEHOLDER_RE.fullmatch(normalized[1:-1].strip()))
    return bool(_PLACEHOLDER_VALUE_RE.fullmatch(normalized)) or bool(
        _ENV_PLACEHOLDER_RE.fullmatch(normalized)
    ) or set(normalized) <= {"x", "*", "."}


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
    project_root = _resolve_project_root(str(data.get("project_root") or "").strip(), profile_dir)

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
            for path_value in (documents.get("license_files") or [])
            if str(path_value or "").strip()
        ],
        "license_text_entries": [
            _clean_text(text_entry)
            for text_entry in (documents.get("license_text_entries") or [])
            if _clean_text(text_entry)
        ],
        "enable_i18n": True
        if settings.get("enable_i18n") is None
        else bool(settings.get("enable_i18n")),
    }


def write_project_profile(path: str | Path, state: dict[str, Any]) -> None:
    target = Path(path)
    data = serialize_project_profile(state)
    errors = validate_project_profile(data)
    if errors:
        raise ValueError("\n".join(errors))
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

    # A profile exported on Windows may carry an absolute drive path while it
    # is imported on Linux/macOS.  pathlib on POSIX treats ``C:/...`` as a
    # relative filename, which would incorrectly produce ``<profile>/C:/...``.
    # Use the profile directory as the portable base on non-Windows hosts.
    if _is_windows_absolute(project_root) and os.name != "nt":
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
    if path.is_absolute() or _is_windows_absolute(value):
        # Keep a foreign-drive path opaque on POSIX; it is still a valid
        # exported Windows path and must not be rebased below the JSON file.
        return str(path) if path.is_absolute() else value.replace("\\", "/")

    base_dir = project_root or profile_dir
    if base_dir is None:
        return value
    return str((base_dir / path).resolve(strict=False))


def _is_windows_absolute(value: str) -> bool:
    """Return whether *value* is a Windows drive/UNC absolute path."""
    return bool(_WINDOWS_ABSOLUTE_RE.match(value)) or value.startswith(("\\\\", "//"))
