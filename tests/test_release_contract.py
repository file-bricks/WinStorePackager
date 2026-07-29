import json
import shutil
from pathlib import Path

import release_contract


ROOT = Path(__file__).resolve().parents[1]


def test_release_contract_is_synchronized_for_the_repository():
    assert release_contract.validate_release_contract(ROOT) == []


def test_missing_dependency_check_has_no_install_side_effect(monkeypatch):
    def missing_module(_: str):
        raise ImportError("not installed")

    monkeypatch.setattr(release_contract.importlib, "import_module", missing_module)

    assert release_contract.missing_runtime_dependencies() == [
        ("Pillow", "PIL"),
        ("pygetwindow", "pygetwindow"),
        ("keyring", "keyring"),
    ]
    assert release_contract.install_command() == "python -m pip install -r requirements.txt"


def test_release_contract_reports_profile_version_drift(tmp_path):
    for filename in (
        "requirements.txt",
        "THIRD_PARTY_LICENSES.txt",
        "pyproject.toml",
        "store_package.json",
        "winstorepackager-project-v1.json",
        "STORE_LISTING.md",
    ):
        shutil.copy(ROOT / filename, tmp_path / filename)

    profile_path = tmp_path / "winstorepackager-project-v1.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile["store"]["changelog"] = "Version 2.3.0: historical release"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    errors = release_contract.validate_release_contract(tmp_path)
    assert any("changelog" in error for error in errors)
