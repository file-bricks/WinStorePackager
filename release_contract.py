"""Reproducible release-contract checks for WinStorePackager.

The module deliberately depends only on the standard library so it can run
before optional GUI dependencies are installed. It keeps source bootstrap,
license provenance, and public Store claims aligned without downloading
packages at application startup.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path


RUNTIME_DEPENDENCIES: dict[str, str] = {
    "Pillow": "PIL",
    "pygetwindow": "pygetwindow",
    "keyring": "keyring",
}

STORE_CLAIMS: dict[str, tuple[str, str]] = {
    "Pillow": ("Icon-Generator", "Icon Generator"),
    "pygetwindow": ("Screenshot-Assistent", "Screenshot Assistant"),
    "keyring": ("Keyring-Integration", "Keyring Integration"),
}


def _normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _declared_requirements(path: Path) -> set[str]:
    names: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", ".")):
            continue
        match = re.match(r"[A-Za-z0-9_.-]+", line)
        if match:
            names.add(_normalized_name(match.group(0)))
    return names


def _licensed_dependencies(path: Path) -> set[str]:
    names: set[str] = set()
    for block in re.split(r"\r?\n\s*\r?\n", path.read_text(encoding="utf-8")):
        lines = block.splitlines()
        if lines and "License:" in block:
            names.add(_normalized_name(lines[0].strip()))
    return names


def _project_version(path: Path) -> str:
    match = re.search(
        r'^version\s*=\s*"([0-9]+(?:\.[0-9]+){2})"',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError("[project].version fehlt oder ist nicht semver-kompatibel")
    return match.group(1)


def missing_runtime_dependencies() -> list[tuple[str, str]]:
    """Return missing package/import pairs without mutating the environment."""
    missing: list[tuple[str, str]] = []
    for package_name, import_name in RUNTIME_DEPENDENCIES.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append((package_name, import_name))
    return missing


def install_command() -> str:
    """The single reproducible setup command shown to source users."""
    return "python -m pip install -r requirements.txt"


def validate_release_contract(root: Path) -> list[str]:
    """Return source, license, profile, and Store-metadata drift errors."""
    root = Path(root)
    errors: list[str] = []
    expected_dependencies = {_normalized_name(name) for name in RUNTIME_DEPENDENCIES}

    requirements = _declared_requirements(root / "requirements.txt")
    missing_requirements = expected_dependencies - requirements
    if missing_requirements:
        errors.append(f"requirements.txt fehlt: {', '.join(sorted(missing_requirements))}")

    licensed_dependencies = _licensed_dependencies(root / "THIRD_PARTY_LICENSES.txt")
    missing_licenses = expected_dependencies - licensed_dependencies
    if missing_licenses:
        errors.append(f"THIRD_PARTY_LICENSES.txt fehlt: {', '.join(sorted(missing_licenses))}")

    project_version = _project_version(root / "pyproject.toml")
    expected_store_version = f"{project_version}.0"
    store_package = json.loads((root / "store_package.json").read_text(encoding="utf-8"))
    profile = json.loads((root / "winstorepackager-project-v1.json").read_text(encoding="utf-8"))
    profile_metadata = profile.get("metadata", {})
    profile_store = profile.get("store", {})

    if store_package.get("version") != expected_store_version:
        errors.append(
            f"store_package.json version muss {expected_store_version} sein, ist aber {store_package.get('version')!r}"
        )
    if profile_metadata.get("version") != expected_store_version:
        errors.append("Projektprofil-Version stimmt nicht mit pyproject.toml überein")
    if profile_metadata.get("app_name") != store_package.get("app_name"):
        errors.append("Projektprofil und store_package.json weichen bei app_name ab")
    for field in ("privacy_url", "support_url", "category", "age_rating"):
        if profile_store.get(field) != store_package.get(field):
            errors.append(f"Projektprofil und store_package.json weichen bei {field} ab")

    source_path = str(profile.get("paths", {}).get("source_path", ""))
    if source_path and project_version not in source_path:
        errors.append("Projektprofil source_path trägt nicht die aktuelle pyproject-Version")
    if expected_store_version not in str(profile_store.get("changelog", "")):
        errors.append("Projektprofil changelog trägt nicht die aktuelle Store-Version")

    german_section, english_section = (root / "STORE_LISTING.md").read_text(encoding="utf-8").split("## English", 1)
    for german_claim, english_claim in STORE_CLAIMS.values():
        if german_claim.lower() not in german_section.lower() or english_claim.lower() not in english_section.lower():
            errors.append(
                f"STORE_LISTING.md enthält die Claims {german_claim!r}/{english_claim!r} nicht in beiden Sprachen"
            )

    return errors
