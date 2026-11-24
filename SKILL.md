---
name: winstorepackager
version: 3.1.0
description: Prepare Python desktop applications for Microsoft Store submission (AppxManifest.xml, Store tile icons, redacted project profiles, readiness checks, and Windows SDK MSIX packaging/signing).
---

# WinStorePackager — Product Skill

Use this skill when an agent assists a user in preparing, validating, or packaging a Python desktop application for the Microsoft Store with **WinStorePackager (`v3.1.0`)**.

> **Boundary:** `SKILL.md` describes product usage for end users and assistant agents. It works standalone after cloning/downloading this repository and requires no external workspace or private paths.

---

## 1. Capabilities & Scope

- **Supported version:** `3.1.0` (`pyproject.toml`; Store submission metadata in `store_package.json`: `3.1.0.0`)
- **What WinStorePackager does:**
  - Generates schema-valid `AppxManifest.xml` (separating general `<Capability>`, `<uap:Capability>`, and `<rescap:Capability>` such as `runFullTrust`, plus `<Resources>` language declarations).
  - Generates required Microsoft Store tile icons (`44x44`, `50x50`, `150x150`, `310x310`, `310x150`) with Lanczos resampling.
  - Imports and exports redacted portable project profiles (`winstorepackager-project-v1.json`) that exclude Publisher DNs, certificate paths, passwords, and Windows SDK paths.
  - Invokes Windows SDK `makeappx.exe` and `signtool.exe` (SHA-256) with OS Keyring password retrieval and deterministic WACK XML report parsing (`parse_wack_report`).
  - Provides SDK-free cross-platform preflight checks (`unix_preflight.py`) and Store readiness checks (`scripts/check_store_readiness.py`) usable on Linux, macOS, and Windows.
  - Provides a 6-language GUI (`DE`, `EN`, `ES`, `ZH`, `JA`, `RU`) via `WindowsStorePublisher_3.py` and translation catalog validation (`manage_translations.py --check`).
- **What WinStorePackager does NOT do:**
  - It is not the official Microsoft MSIX Packaging Tool and does not upload or submit packages directly to Microsoft Partner Center.
  - Building signed `.msix` packages and running WACK (`appcert.exe`) require Windows + Windows SDK; Linux and macOS support SDK-free preflight and profile validation only.

---

## 2. Prerequisites & Installation

- **Python:** `>=3.9` (tested on `3.9`–`3.13`)
- **Runtime dependencies (`requirements.txt`):** `Pillow>=12.3.0`, `pygetwindow>=0.0.9`, `keyring>=25.0.0`
- **Install from source:**

```bash
python -m pip install -r requirements.txt
```

- **Windows runtime state:** Host-local settings (`settings_store_packager.json`) and rotating logs are stored outside the repository under `%LOCALAPPDATA%\WinStorePackager` (Windows), `~/Library/Application Support/WinStorePackager` (macOS), or `${XDG_CONFIG_HOME:-~/.config}/winstorepackager` (Linux). Certificate passwords stay in the OS Keyring.

---

## 3. Machine-Callable Commands & Workflows

### A. Cross-Platform Preflight (`unix_preflight.py`)

Validate repository structure, `store_package.json`, documentation, icons/screenshots, and an optional `winstorepackager-project-v1.json` profile without Windows SDK binaries:

```bash
python unix_preflight.py --project-root . --json
python unix_preflight.py --project-root . --profile-path ./winstorepackager-project-v1.json --json
```

- **Exit codes:** `0` = no errors (`"ok": true` in JSON output), `1` = validation errors (`"errors": [...]`).
- **Readback:** Parse JSON stdout (`platform`, `ok`, `errors`, `warnings`, `checked`).

### B. Store Readiness Check (`scripts/check_store_readiness.py`)

Validate Microsoft Store listing sections, 7-keyword limits (Policy 10.1.3), staged listing files, Store icon assets, and live URL reachability:

```bash
python scripts/check_store_readiness.py
```

- **Exit codes:** `0` = all checks passed, `1` = readiness errors detected.

### C. Translation Catalog Gate (`manage_translations.py`)

Verify 100% 6-language parity (`de`, `en`, `es`, `zh`, `ja`, `ru`) without modifying `locales/translations.json`:

```bash
python manage_translations.py --dir . --check
```

- **Exit codes:** `0` = 100% parity across all 6 languages, `1` = missing translations or invalid/unreadable JSON (fail-closed).

### D. Human GUI Launch (`WindowsStorePublisher_3.py` / `START.bat`)

Start the interactive desktop application (requires a graphical display; on Windows `START.bat` launches without keeping a console open):

```bash
python WindowsStorePublisher_3.py
```

- **Keyboard shortcuts:** `F1` (Accessibility & Shortcut Help), `Shift+F1` (About), `F5` (Preflight Check), `Ctrl+1..4` (Tabs), `Ctrl+PageDown` / `Ctrl+PageUp` (Cycle Tabs), `Ctrl+O` / `Ctrl+E` (Import/Export Profile), `Ctrl+S` (Save Settings).

---

## 4. Safety, Privacy & Side Effects

- **Secrets & Redaction:** Never write real Publisher DNs (`CN=...`), `.pfx`/`.p12` paths, passwords, or Windows SDK tool paths into `winstorepackager-project-v1.json` or Git-tracked files. `project_profile.py` (`validate_project_profile`, `write_project_profile`) rejects sensitive values before creating output files.
- **Non-Elevation:** Normal operation and MSIX packaging run without Administrator privileges (`RunAsInvoker`). Only an optional WACK (`appcert.exe`) run requires elevation by Windows itself.
- **Zero-Egress:** WinStorePackager sends no telemetry. External network calls occur only if the user explicitly triggers timestamping during `signtool.exe sign` or URL reachability checks.

---

## 5. Verification

Run the automated test suite and linters from the repository root:

```bash
python -m pytest -ra -v
ruff check .
python -m compileall -q .
```

## 6. Further References

- Canonical LLM overview: [`llms.txt`](llms.txt)
- Profile schema specification: [`PROJECT_PROFILE_FORMAT.md`](PROJECT_PROFILE_FORMAT.md)
- Privacy boundary: [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md)
- Security policy & SLAs: [`SECURITY.md`](SECURITY.md)
- Store preparation checklist: [`WINDOWS_STORE_PREP.md`](WINDOWS_STORE_PREP.md)
