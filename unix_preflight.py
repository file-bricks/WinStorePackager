from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from project_profile import read_project_profile

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
URL_PREFIXES = ("http://", "https://")


def run_unix_preflight(
    project_root: str | Path,
    *,
    profile_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve(strict=False)
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    if not root.exists():
        raise FileNotFoundError(f"Projektpfad existiert nicht: {root}")

    _require_file(root / "WindowsStorePublisher_3.py", "Hauptskript", errors, checked)
    _require_file(root / "requirements.txt", "Requirements", errors, checked)
    _require_file(root / "README.md", "README", errors, checked)
    _require_file(root / "PRIVACY_POLICY.md", "Privacy Policy", errors, checked)
    _require_file(root / "STORE_LISTING.md", "Store-Listing", errors, checked)
    _require_file(root / "PROJECT_PROFILE_FORMAT.md", "Projektprofilformat", errors, checked)
    _require_file(root / "LICENSE", "Lizenzdatei", errors, checked)
    _require_file(root / "store_package.json", "Store-Paket-Metadaten", errors, checked)

    _require_any_file(
        [
            root / "WinStorePackager.ico",
            root / "WinstorePackager_icon.jpg",
            root / "README" / "screenshots" / "main.png",
        ],
        "Icon-/Screenshot-Artefakte",
        warnings,
        checked,
    )

    readme_text = _read_text(root / "README.md")
    if readme_text and "Microsoft Store" not in readme_text:
        warnings.append("README erwähnt den Microsoft Store nicht explizit.")

    privacy_text = _read_text(root / "PRIVACY_POLICY.md")
    if privacy_text and "local" not in privacy_text.lower() and "lokal" not in privacy_text.lower():
        warnings.append("Privacy Policy erklärt die lokale Datenhaltung nicht klar.")

    listing_text = _read_text(root / "STORE_LISTING.md")
    if listing_text and "support" not in listing_text.lower() and "support-url" not in listing_text.lower():
        warnings.append("Store-Listing erwähnt keine Support-Informationen.")

    store_package = _load_json(root / "store_package.json", errors)
    if store_package:
        _validate_store_package(store_package, errors, warnings)

    if profile_path:
        checked.append(str(Path(profile_path)))
        try:
            profile = read_project_profile(profile_path)
        except Exception as exc:
            errors.append(f"Projektprofil ist ungültig: {exc}")
        else:
            _validate_profile_state(profile, store_package, errors, warnings)

    platform_name = "macos" if sys.platform == "darwin" else ("linux" if sys.platform.startswith("linux") else "unix")

    return {
        "platform": platform_name,
        "project_root": str(root),
        "profile_path": str(Path(profile_path).resolve(strict=False)) if profile_path else None,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def format_report(report: dict[str, Any]) -> str:
    platform_label = "macOS" if report["platform"] == "macos" else ("Linux" if report["platform"] == "linux" else "Unix")
    lines = [
        f"{platform_label}-Preflight für WinStorePackager",
        f"Projekt: {report['project_root']}",
        "",
    ]
    if report["errors"]:
        lines.append("Fehler:")
        lines.extend(f"- {item}" for item in report["errors"])
        lines.append("")
    if report["warnings"]:
        lines.append("Warnungen:")
        lines.extend(f"- {item}" for item in report["warnings"])
        lines.append("")
    if not report["errors"] and not report["warnings"]:
        lines.append("Keine Befunde.")
        lines.append("")
    lines.append(f"Geprüfte Artefakte: {len(report['checked'])}")
    return "\n".join(lines)


def _require_file(path: Path, label: str, errors: list[str], checked: list[str]) -> None:
    checked.append(str(path))
    if not path.is_file():
        errors.append(f"{label} fehlt: {path.name}")


def _require_any_file(paths: list[Path], label: str, warnings: list[str], checked: list[str]) -> None:
    checked.extend(str(path) for path in paths)
    if not any(path.is_file() for path in paths):
        warnings.append(f"{label} fehlen vollständig.")


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name} ist kein gültiges UTF-8-JSON: {exc}")
        return {}


def _validate_store_package(data: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if not str(data.get("app_name", "")).strip():
        errors.append("store_package.json: `app_name` fehlt.")

    version = str(data.get("version", "")).strip()
    if not VERSION_RE.match(version):
        errors.append(f"store_package.json: Version hat falsches Format: {version!r}")

    executable = str(data.get("executable", "")).strip()
    if not executable.endswith(".exe"):
        errors.append("store_package.json: `executable` muss auf `.exe` enden.")

    description = str(data.get("description", "")).strip()
    if not description:
        warnings.append("store_package.json: Beschreibung fehlt.")

    for key in ("privacy_url", "support_url"):
        value = str(data.get(key, "")).strip()
        if not value:
            errors.append(f"store_package.json: `{key}` fehlt.")
        elif not value.startswith(URL_PREFIXES):
            errors.append(f"store_package.json: `{key}` muss mit http:// oder https:// beginnen.")

    if not str(data.get("category", "")).strip():
        warnings.append("store_package.json: Kategorie fehlt.")
    if not str(data.get("age_rating", "")).strip():
        warnings.append("store_package.json: Altersfreigabe fehlt.")


def _validate_profile_state(
    profile: dict[str, Any],
    store_package: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    for key in ("script_path", "icon_path"):
        value = str(profile.get(key, "")).strip()
        if not value:
            errors.append(f"Projektprofil: `{key}` fehlt.")
            continue
        if not Path(value).exists():
            errors.append(f"Projektprofil: `{key}` zeigt ins Leere: {value}")

    exe_name = str(profile.get("exe_name", "")).strip()
    if not exe_name.endswith(".exe"):
        errors.append("Projektprofil: `exe_name` muss auf `.exe` enden.")

    profile_app_name = str(profile.get("app_name", "")).strip()
    package_app_name = str(store_package.get("app_name", "")).strip()
    if profile_app_name and package_app_name and profile_app_name != package_app_name:
        warnings.append(
            "Projektprofil: `app_name` stimmt nicht mit `store_package.json` überein."
        )

    profile_version = str(profile.get("version", "")).strip()
    package_version = str(store_package.get("version", "")).strip()
    if profile_version and package_version and profile_version != package_version:
        warnings.append(
            "Projektprofil: `version` stimmt nicht mit `store_package.json` überein."
        )

    for key in ("privacy_url", "support_url"):
        profile_value = str(profile.get(key, "")).strip()
        package_value = str(store_package.get(key, "")).strip()
        if profile_value and package_value and profile_value != package_value:
            warnings.append(
                f"Projektprofil: `{key}` weicht von `store_package.json` ab."
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SDK-freier Unix-Preflight (Linux/macOS) für WinStorePackager-Repositories."
    )
    parser.add_argument(
        "--project-root",
        default=Path(__file__).resolve(strict=False).parent,
        help="Projektwurzel mit README, Store-Dokumenten und store_package.json",
    )
    parser.add_argument(
        "--profile-path",
        help="Optionaler Pfad zu einem `winstorepackager-project-v1.json`",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Bericht als JSON ausgeben",
    )
    args = parser.parse_args(argv)

    report = run_unix_preflight(args.project_root, profile_path=args.profile_path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_report(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
