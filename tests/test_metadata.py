"""Contract tests for WinStorePackager repository metadata, discoverability, and documentation parity."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_badges_and_quick_nav() -> None:
    """Verify badges and quick navigation in both English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "License-MIT" in readme or "Lizenz-MIT" in readme or "License: MIT" in readme or "Lizenz: MIT" in readme, f"License badge missing in {lang}"
        assert "Version-3.1.0" in readme or "3.1.0" in readme, f"Version badge missing in {lang}"
        assert "Zero--Egress" in readme or "Zero-Egress" in readme or "Local--First" in readme or "Local-First" in readme, f"Privacy badge missing in {lang}"
        assert "file--bricks" in readme or "file-bricks" in readme, f"Ecosystem badge missing in {lang}"
        assert "open--bricks" in readme or "open-bricks" in readme, f"Umbrella badge missing in {lang}"
        assert "llms.txt" in readme, f"llms.txt badge/link missing in {lang}"
        assert "SECURITY.md" in readme, f"SECURITY.md link missing in {lang}"
        assert "CHANGELOG.md" in readme, f"CHANGELOG.md link missing in {lang}"
        assert "PROJECT_PROFILE_FORMAT.md" in readme, f"PROJECT_PROFILE_FORMAT.md link missing in {lang}"


def test_mermaid_diagrams_in_readmes() -> None:
    """Verify Mermaid architecture and sequence lifecycle diagrams exist in READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "```mermaid" in readme, f"Mermaid block missing in {lang}"
        assert "graph TD" in readme or "flowchart TD" in readme, f"Architecture diagram missing in {lang}"
        assert "sequenceDiagram" in readme, f"Sequence lifecycle diagram missing in {lang}"
        assert "makeappx" in readme, f"makeappx step missing in sequence diagram for {lang}"
        assert "signtool" in readme, f"signtool step missing in sequence diagram for {lang}"


def test_visual_showcase_screenshots_exist() -> None:
    """Verify all screenshots referenced in README visual showcase exist on disk."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    matches = re.findall(r'!\[.*?\]\((releases/windowsstore/screenshots/[^\)]+)\)', readme_en)
    assert len(matches) >= 4, f"Expected at least 4 showcase screenshots in README.md, found {len(matches)}"

    for rel_path in matches:
        full_path = ROOT / rel_path
        assert full_path.is_file(), f"Screenshot file {rel_path} does not exist"
        assert full_path.stat().st_size > 0, f"Screenshot file {rel_path} is empty"


def test_security_policy_bilingual_integrity() -> None:
    """Verify SECURITY.md contains English and German sections, local-first guarantees, SLAs, and contact emails."""
    security_file = ROOT / "SECURITY.md"
    assert security_file.is_file(), "SECURITY.md must exist"
    content = security_file.read_text(encoding="utf-8")

    assert "## Deutsch" in content or "## German" in content, "German section missing in SECURITY.md"
    assert "## English" in content, "English section missing in SECURITY.md"
    assert "Zero-Egress" in content or "Local-First" in content, "Local-first guarantee missing in SECURITY.md"
    assert "Keyring" in content or "keyring" in content, "Keyring credential security missing in SECURITY.md"
    assert "security@open-bricks.org" in content, "Umbrella security contact email missing in SECURITY.md"
    assert "security@file-bricks.org" in content, "Security contact email missing in SECURITY.md"
    assert "security/advisories/new" in content, "Vulnerability reporting instructions missing"
    assert "48" in content, "48h response SLA missing in SECURITY.md"
    assert "5" in content, "5-day triage commitment missing in SECURITY.md"


def test_llms_txt_integrity() -> None:
    """Verify llms.txt contains updated last-checked timestamp and repository context."""
    llms_file = ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt must exist"
    content = llms_file.read_text(encoding="utf-8")

    assert any(
        ts in content
        for ts in ["Last-checked: 2026-09-26", "Last-checked: 2026-09-21", "Last-checked: 2026-09-13", "Last-checked: 2026-09-11"]
    ), "llms.txt timestamp not updated"
    assert "https://github.com/file-bricks/WinStorePackager" in content, "Canonical repo link missing in llms.txt"
    assert "MSIX" in content and "AppxManifest" in content, "Packaging keywords missing in llms.txt"
    assert "SECURITY.md" in content, "SECURITY.md reference missing in llms.txt"
    assert "NOTICE" in content, "NOTICE reference missing in llms.txt"
    assert "THIRD_PARTY_LICENSES.md" in content, "THIRD_PARTY_LICENSES.md reference missing in llms.txt"
    assert "MARKETING-LOG.txt" in content, "MARKETING-LOG.txt reference missing in llms.txt"


def test_sibling_ecosystem_matrix() -> None:
    """Verify sibling tools matrix linking to file-bricks, doc-bricks, ellmos-ai, and open-bricks."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "ProSync" in readme, f"ProSync sibling link missing in {lang}"
        assert "CleanMarkdown" in readme, f"CleanMarkdown sibling link missing in {lang}"
        assert "DokuZen" in readme, f"DokuZen sibling link missing in {lang}"
        assert "UniversalDocsGrabber" in readme, f"UniversalDocsGrabber sibling link missing in {lang}"
        assert "open-bricks" in readme, f"open-bricks umbrella link missing in {lang}"


def test_pyproject_pep621_metadata() -> None:
    """Verify pyproject.toml PEP 621 metadata, urls, and classifiers."""
    pyproject_file = ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml must exist"
    content = pyproject_file.read_text(encoding="utf-8")

    assert 'name = "winstorepackager"' in content
    assert 'version = "3.1.0"' in content
    assert "Security =" in content, "Security URL missing in pyproject.toml"
    assert "Notice =" in content, "Notice URL missing in pyproject.toml"
    assert "Homepage =" in content, "Homepage URL missing in pyproject.toml"
    assert "Repository =" in content, "Repository URL missing in pyproject.toml"
    assert "Documentation =" in content, "Documentation URL missing in pyproject.toml"
    assert "Changelog =" in content, "Changelog URL missing in pyproject.toml"
    assert "Umbrella =" in content, "Umbrella URL missing in pyproject.toml"
    assert '"Parent Organization"' in content, "Parent Organization URL missing in pyproject.toml"
    assert '"Umbrella Ecosystem"' in content, "Umbrella Ecosystem URL missing in pyproject.toml"
    assert "Operating System :: Microsoft :: Windows" in content
    assert "Operating System :: OS Independent" in content, "OS Independent classifier missing"
    assert "Programming Language :: Python :: 3.13" in content, "Python 3.13 classifier missing"
    assert "license-files =" in content, "license-files missing in pyproject.toml"
    assert "minversion =" in content, "minversion missing in pyproject.toml"
    assert "norecursedirs =" in content, "norecursedirs missing in pyproject.toml"
    assert (
        'addopts = "-ra -v --basetemp=.pytest_temp"' in content
        or 'addopts = "-ra -v"' in content
        or 'addopts = "-v"' in content
    ), "pytest addopts missing in pyproject.toml"


def test_ci_workflow_integrity() -> None:
    """Verify GitHub Actions CI workflows exist, have multi-OS matrix, concurrency, and compileall gate."""
    workflow_dir = ROOT / ".github" / "workflows"
    assert (workflow_dir / "ci.yml").is_file(), "ci.yml missing"

    ci_yml = (workflow_dir / "ci.yml").read_text(encoding="utf-8")
    assert "ubuntu-latest" in ci_yml and "windows-latest" in ci_yml and "macos-latest" in ci_yml
    assert "3.13" in ci_yml, "Python 3.13 missing from CI matrix"
    assert "concurrency:" in ci_yml, "Concurrency block missing in ci.yml"
    assert "cancel-in-progress: true" in ci_yml, "cancel-in-progress missing in ci.yml"
    assert "python -m compileall -q ." in ci_yml, "compileall bytecode gate missing in ci.yml"
    assert "ruff check ." in ci_yml
    assert "pytest -v" in ci_yml or "pytest -ra -v" in ci_yml


def test_gitignore_hardening() -> None:
    """Verify .gitignore contains multi-host sync conflict patterns and multi-agent locks."""
    gitignore_file = ROOT / ".gitignore"
    assert gitignore_file.is_file(), ".gitignore must exist"
    content = gitignore_file.read_text(encoding="utf-8")

    assert "*.sync-conflict-*" in content, "sync-conflict pattern missing in .gitignore"
    assert "*.conflict" in content, "conflict pattern missing in .gitignore"
    assert "*-CONFLIT-*" in content, "CONFLIT pattern missing in .gitignore"
    assert "LOCK.*" in content, "LOCK.* pattern missing in .gitignore"
    assert "*.lock" in content, "*.lock pattern missing in .gitignore"
    assert "wheelhouse/" in content, "wheelhouse pattern missing in .gitignore"
    assert ".wheel-smoke/" in content, ".wheel-smoke pattern missing in .gitignore"


def test_bilingual_readme_15_point_navigation_parity() -> None:
    """Verify exact 15-point quick navigation and matching section headers in English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    en_anchors = [
        "#quick-start",
        "#features",
        "#architecture--packaging-pipeline",
        "#packaging-lifecycle-flow",
        "#governance--runtime-invariants",
        "#visual-showcase--store-assets",
        "#project-profiles",
        "#prerequisites--installation",
        "#sdk-free-unix-preflight",
        "#local-data-and-security",
        "#sibling-tools--ecosystem",
        "#comparison-with-alternatives",
        "#third-party-licenses--transparency",
        "#marketing--target-personas",
        "#documentation--license",
    ]

    de_anchors = [
        "#schnellstart",
        "#funktionen",
        "#architektur--paketierungs-pipeline",
        "#paketierungs-lebenszyklus",
        "#governance--laufzeit-invarianten",
        "#visuelle-showcase--store-assets",
        "#projektprofile",
        "#voraussetzungen--installation",
        "#sdk-freier-unix-preflight",
        "#lokale-daten-und-sicherheit",
        "#geschwister-tools--ökosystem",
        "#vergleich-mit-alternativen",
        "#drittanbieter-lizenzen--transparenz",
        "#marketing--zielgruppen",
        "#dokumentation--lizenz",
    ]

    assert len(en_anchors) == 15, "English anchors list must have 15 elements"
    assert len(de_anchors) == 15, "German anchors list must have 15 elements"

    for anchor in en_anchors:
        assert f'href="{anchor}"' in readme_en, f"Anchor {anchor} missing in README.md navigation bar"

    for anchor in de_anchors:
        assert f'href="{anchor}"' in readme_de, f"Anchor {anchor} missing in README_de.md navigation bar"


def test_governance_invariants_table_parity() -> None:
    """Verify all 10 governance and runtime invariants (INV-LOCAL-01 to INV-SLA-10) are present in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    invariants = [
        "INV-LOCAL-01",
        "INV-SEC-02",
        "INV-STORE-03",
        "INV-ASSET-04",
        "INV-PROFILE-05",
        "INV-CROSS-06",
        "INV-STATE-07",
        "INV-WACK-08",
        "INV-I18N-09",
        "INV-SLA-10",
    ]

    for inv in invariants:
        assert inv in readme_en, f"Invariant {inv} missing in README.md"
        assert inv in readme_de, f"Invariant {inv} missing in README_de.md"


def test_third_party_licenses_md_integrity() -> None:
    """Verify THIRD_PARTY_LICENSES.md exists, is comprehensive, and covers all required packages and invariants."""
    lic_md = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_md.is_file(), "THIRD_PARTY_LICENSES.md must exist"
    content = lic_md.read_text(encoding="utf-8")

    for pkg in ["Pillow", "keyring", "pygetwindow", "PyInstaller", "pytest", "ruff", "pywin32-ctypes"]:
        assert pkg in content, f"Package {pkg} missing in THIRD_PARTY_LICENSES.md"

    for term in ["Zero Egress", "RunAsInvoker", "HPND-sell-variant", "MIT", "BSD-3-Clause", "Bootloader"]:
        assert term in content, f"Term/concept {term} missing in THIRD_PARTY_LICENSES.md"


def test_marketing_log_contract() -> None:
    """Verify MARKETING-LOG.txt exists, is active, and contains target personas, search terms, and 10 invariants."""
    m_log = ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file(), "MARKETING-LOG.txt must exist"
    content = m_log.read_text(encoding="utf-8")

    assert "ACTIVE / PFAD B DISCOVERABILITY & MARKETING VERIFIED" in content
    assert "TARGET PERSONAS" in content
    assert "Solo Python Desktop App Developers" in content
    assert "Enterprise & Commercial Python ISVs" in content
    assert "Open-Source Maintainers" in content
    assert "Privacy-Conscious & Local-First Desktop Engineers" in content
    assert "COMPETITIVE COMPARISON MATRIX" in content
    assert "HIGH-INTENT SEARCH TERM MATRIX" in content
    for inv in ["INV-LOCAL-01", "INV-SEC-02", "INV-STORE-03", "INV-ASSET-04", "INV-PROFILE-05",
                "INV-CROSS-06", "INV-STATE-07", "INV-WACK-08", "INV-I18N-09", "INV-SLA-10"]:
        assert inv in content, f"Invariant {inv} missing in MARKETING-LOG.txt"


def test_pyproject_extended_urls() -> None:
    """Verify pyproject.toml contains all extended Pfad B project URLs."""
    pyproject_file = ROOT / "pyproject.toml"
    assert pyproject_file.is_file()
    content = pyproject_file.read_text(encoding="utf-8")

    assert '"Third-Party Licenses"' in content
    assert '"Marketing Log"' in content
    assert '"LLM Ready"' in content


def test_changelog_pfad_b_entry() -> None:
    """Verify CHANGELOG.md contains recent Pfad B release notes."""
    changelog_file = ROOT / "CHANGELOG.md"
    assert changelog_file.is_file()
    content = changelog_file.read_text(encoding="utf-8")

    assert "Discoverability, Visual Architecture & Marketing Overhaul" in content or "Discoverability, Visual Architecture & Metadata Parity Overhaul" in content
    assert "Pfad B, 2026-09-21" in content or "Pfad B, 2026-09-11" in content


def test_ci_timeout_and_concurrency_guardrails() -> None:
    """Verify runaway timeout-minutes and concurrency guardrails in all CI workflows."""
    workflow_dir = ROOT / ".github" / "workflows"

    # Main CI
    ci_yml = (workflow_dir / "ci.yml").read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in ci_yml, "ci.yml missing 15 min timeout"
    assert "concurrency:" in ci_yml, "ci.yml missing concurrency block"
    assert "cancel-in-progress: true" in ci_yml, "ci.yml missing cancel-in-progress"

    # Source Platform Smoke
    smoke_yml = (workflow_dir / "source-platform-smoke.yml").read_text(encoding="utf-8")
    assert "timeout-minutes: 10" in smoke_yml, "source-platform-smoke.yml missing 10 min timeout"
    assert "concurrency:" in smoke_yml, "source-platform-smoke.yml missing concurrency block"
    assert "cancel-in-progress: true" in smoke_yml, "source-platform-smoke.yml missing cancel-in-progress"

    # Welcome Workflow
    welcome_yml = (workflow_dir / "welcome.yml").read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_yml, "welcome.yml must use first-interaction@v3"
    assert "timeout-minutes: 5" in welcome_yml, "welcome.yml missing 5 min timeout"
    assert "concurrency:" in welcome_yml, "welcome.yml missing concurrency block"
    assert "cancel-in-progress: true" in welcome_yml, "welcome.yml missing cancel-in-progress"

    # Stale Workflow
    stale_yml = (workflow_dir / "stale.yml").read_text(encoding="utf-8")
    assert "timeout-minutes: 10" in stale_yml, "stale.yml missing 10 min timeout"
    assert "concurrency:" in stale_yml, "stale.yml missing concurrency block"
    assert "cancel-in-progress: true" in stale_yml, "stale.yml missing cancel-in-progress"


def test_extended_gitignore_sync_and_lock_defense() -> None:
    """Verify .gitignore contains extended multi-host sync and lock protection patterns."""
    gitignore_file = ROOT / ".gitignore"
    assert gitignore_file.is_file(), ".gitignore must exist"
    content = gitignore_file.read_text(encoding="utf-8")

    for pat in [
        "*-WORKSTATION*",
        "*-ASUS-GEI*",
        "*-MacBook*",
        "*-IDEAPAD*",
        "* (kopie)*",
        "* (copy)*",
        "*conflicted copy*",
        "LOCK",
        "LOCK.*",
        "LOCK.user.*",
        "*.lock",
        "!package-lock.json",
        "LOCK.permissions.json",
        ".automation-lock",
        "uv.lock",
        ".pytest_temp/",
        "wheelhouse/",
        ".wheel-smoke/",
        ".coverage*",
        "htmlcov/",
    ]:
        assert pat in content, f"Pattern {pat} missing in .gitignore"


def test_changelog_recent_pfad_a_entry() -> None:
    """Verify CHANGELOG.md contains recent Pfad A hygiene release and maintenance notes."""
    changelog_file = ROOT / "CHANGELOG.md"
    assert changelog_file.is_file()
    content = changelog_file.read_text(encoding="utf-8")

    assert "Pfad A" in content, "Pfad A marker missing in CHANGELOG.md"
    assert "2026-09-13" in content, "2026-09-13 date missing in CHANGELOG.md"
    assert "CI" in content and ("Härtung" in content or "Hardening" in content or "Hygiene" in content)


def test_bilingual_readme_reciprocal_dual_anchors() -> None:
    """Verify that both README.md and README_de.md contain reciprocal HTML anchors for all 15 sections."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    pairs = [
        ("quick-start", "schnellstart"),
        ("features", "funktionen"),
        ("architecture--packaging-pipeline", "architektur--paketierungs-pipeline"),
        ("packaging-lifecycle-flow", "paketierungs-lebenszyklus"),
        ("governance--runtime-invariants", "governance--laufzeit-invarianten"),
        ("visual-showcase--store-assets", "visuelle-showcase--store-assets"),
        ("project-profiles", "projektprofile"),
        ("prerequisites--installation", "voraussetzungen--installation"),
        ("sdk-free-unix-preflight", "sdk-freier-unix-preflight"),
        ("local-data-and-security", "lokale-daten-und-sicherheit"),
        ("sibling-tools--ecosystem", "geschwister-tools--ökosystem"),
        ("comparison-with-alternatives", "vergleich-mit-alternativen"),
        ("third-party-licenses--transparency", "drittanbieter-lizenzen--transparenz"),
        ("marketing--target-personas", "marketing--zielgruppen"),
        ("documentation--license", "dokumentation--lizenz"),
    ]

    for en_id, de_id in pairs:
        assert f'<a id="{en_id}"></a>' in readme_en, f'Anchor <a id="{en_id}"></a> missing in README.md'
        assert f'<a id="{de_id}"></a>' in readme_en, f'Reciprocal anchor <a id="{de_id}"></a> missing in README.md'
        assert f'<a id="{en_id}"></a>' in readme_de, f'Reciprocal anchor <a id="{en_id}"></a> missing in README_de.md'
        assert f'<a id="{de_id}"></a>' in readme_de, f'Anchor <a id="{de_id}"></a> missing in README_de.md'


def test_third_party_licenses_invariant_matrix() -> None:
    """Verify THIRD_PARTY_LICENSES.md includes the Invariant Cross-Reference Matrix and all 10 invariants."""
    lic_md = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_md.is_file()
    content = lic_md.read_text(encoding="utf-8")

    assert "### Invariant Cross-Reference Matrix" in content
    for inv in [
        "INV-LOCAL-01", "INV-SEC-02", "INV-STORE-03", "INV-ASSET-04", "INV-PROFILE-05",
        "INV-CROSS-06", "INV-STATE-07", "INV-WACK-08", "INV-I18N-09", "INV-SLA-10",
    ]:
        assert inv in content, f"Invariant {inv} missing in THIRD_PARTY_LICENSES.md matrix"


def test_marketing_log_pfad_b_audit_section() -> None:
    """Verify MARKETING-LOG.txt contains the 2026-09-21 Pfad B audit section and full topic list."""
    m_log = ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file()
    content = m_log.read_text(encoding="utf-8")

    assert "DISCOVERABILITY, MARKETING & GOVERNANCE AUDIT (PFAD B, 2026-09-21)" in content
    assert "20/20" in content
    assert "zero-egress" in content
    assert "open-bricks" in content


def test_canonical_notice_file_contract() -> None:
    """Verify root NOTICE file exists, is non-empty, and provides canonical open-source attribution."""
    notice_file = ROOT / "NOTICE"
    assert notice_file.is_file(), "NOTICE file must exist in repo root"
    content = notice_file.read_text(encoding="utf-8")

    assert "WinStorePackager" in content, "WinStorePackager title missing in NOTICE"
    assert "Lukas Geiger" in content, "Author missing in NOTICE"
    assert "file-bricks" in content, "file-bricks org missing in NOTICE"
    assert "open-bricks" in content, "open-bricks umbrella missing in NOTICE"
    assert "MIT" in content, "MIT license missing in NOTICE"
    assert "THIRD_PARTY_LICENSES.md" in content, "THIRD_PARTY_LICENSES.md link missing in NOTICE"


def test_changelog_recent_pfad_a_hygiene_entry() -> None:
    """Verify CHANGELOG.md contains the 2026-09-26 Pfad A hygiene release and maintenance notes."""
    changelog_file = ROOT / "CHANGELOG.md"
    assert changelog_file.is_file(), "CHANGELOG.md must exist"
    content = changelog_file.read_text(encoding="utf-8")

    assert "Pfad A, 2026-09-26" in content, "2026-09-26 Pfad A marker missing in CHANGELOG.md"
    assert "welcome.yml" in content, "welcome.yml missing in CHANGELOG.md"
    assert "stale.yml" in content, "stale.yml missing in CHANGELOG.md"
    assert "NOTICE" in content, "NOTICE missing in CHANGELOG.md"


def test_marketing_log_pfad_a_audit_section() -> None:
    """Verify MARKETING-LOG.txt contains Section 8 covering Pfad A 2026-09-26 audit."""
    m_log = ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file(), "MARKETING-LOG.txt must exist"
    content = m_log.read_text(encoding="utf-8")

    assert "8. REPOSITORY HYGIENE, CI LIFECYCLE WORKFLOWS & SBOM RE-AUDIT (PFAD A, 2026-09-26)" in content
    assert "welcome.yml" in content
    assert "NOTICE" in content


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main(["-v", __file__]))
