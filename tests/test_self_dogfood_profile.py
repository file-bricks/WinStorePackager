import json
from pathlib import Path

from project_profile import read_project_profile, validate_project_profile
from unix_preflight import run_unix_preflight


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "winstorepackager-project-v1.json"


def test_self_dogfood_profile_is_valid_and_excludes_local_secrets():
    raw_profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    assert validate_project_profile(raw_profile) == []

    profile_text = json.dumps(raw_profile, ensure_ascii=False)
    assert "CN=" not in profile_text
    assert "makeappx" not in profile_text.lower()
    assert "signtool" not in profile_text.lower()
    assert ".pfx" not in profile_text.lower()
    assert "pfx_password" not in profile_text
    assert "C:\\" not in profile_text

    profile = read_project_profile(PROFILE_PATH)
    assert Path(profile["script_path"]).is_file()
    assert Path(profile["icon_path"]).is_file()
    assert profile["exe_name"] == "WinStorePackager.exe"


def test_self_dogfood_profile_matches_public_store_metadata():
    store_package = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    profile = read_project_profile(PROFILE_PATH)

    assert profile["app_name"] == store_package["app_name"]
    assert profile["version"] == store_package["version"]
    assert profile["privacy_url"] == store_package["privacy_url"]
    assert profile["support_url"] == store_package["support_url"]
    assert profile["category"] == store_package["category"]
    assert profile["age_rating"] == store_package["age_rating"]

    profile_capabilities = {item.strip() for item in profile["capabilities"].split(",")}
    store_capabilities = {item.strip() for item in store_package["capabilities"].split(",")}
    assert profile_capabilities == store_capabilities


def test_unix_preflight_accepts_self_dogfood_profile():
    report = run_unix_preflight(ROOT, profile_path=PROFILE_PATH)

    assert report["ok"] is True, report
    assert report["errors"] == []
