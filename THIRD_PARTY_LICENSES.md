# Third-Party Licenses & Dependency Inventory

**Project:** WinStorePackager  
**Organization:** file-bricks (Umbrella: open-bricks)  
**License:** MIT License  
**Audit Date:** 2026-09-11  
**Status:** Audited & Verified (100% Permissive Open-Source & Compliant Build Exceptions)

---

## Overview

WinStorePackager is designed and developed with strict local-first, zero-egress, and licensing compliance guarantees. All runtime and development dependencies are carefully audited to ensure compatibility with the MIT license and commercial Microsoft Store application distribution.

- **Zero Egress Runtime:** No runtime dependency initiates external telemetry, cloud tracking, or network connections. All packaging, manifest compilation, and icon processing run 100% offline.
- **Unprivileged Execution:** Runs in standard user space (`RunAsInvoker`) without requiring administrator elevation.
- **Secure Credential Storage:** Certificate passwords are kept in OS Keyring and never persisted in plain text or configuration files.

---

## 1. Direct Runtime Dependencies

| Package | SPDX License Identifier | License Name | Upstream URL | Purpose & Security Baseline |
|---|---|---|---|---|
| **Pillow** | HPND-sell-variant | Historical Permission Notice and Disclaimer | https://pypi.org/project/Pillow/ | Multi-scale icon generation, Lanczos resampling (44x44 to 310x310), PNG format validation. Enforces >=12.3.0 vulnerability floor against GHSA-4x4j-2g7c-83w6 and GHSA-45hq-cxwh-f6vc. |
| **keyring** | MIT | MIT License | https://pypi.org/project/keyring/ | Cryptographically secure certificate password storage using OS Keyring (Windows Credential Vault) without plain-text disk storage. Enforces >=25.0.0 floor. |
| **pygetwindow** | BSD-3-Clause | BSD 3-Clause License | https://pypi.org/project/PyGetWindow/ | Window coordinate detection for automated UI screenshot capture and Store listing asset generation. Enforces >=0.0.9 floor. |

---

## 2. Transitive Runtime Dependencies

| Package | SPDX License Identifier | License Name | Upstream URL | Purpose |
|---|---|---|---|---|
| **PyRect** | BSD-3-Clause | BSD 3-Clause License | https://pypi.org/project/PyRect/ | 2D rectangle and geometry calculations for PyGetWindow window bounding boxes. |
| **jaraco.classes** | MIT | MIT License | https://pypi.org/project/jaraco.classes/ | Class and metaclass utility routines for keyring backend dispatching. |
| **jaraco.context** | MIT | MIT License | https://pypi.org/project/jaraco.context/ | Context manager helpers for keyring credential operations. |
| **jaraco.functools** | MIT | MIT License | https://pypi.org/project/jaraco.functools/ | Function decoration and caching utilities for keyring credential retrieval. |
| **pywin32-ctypes** | BSD-3-Clause | BSD 3-Clause License | https://pypi.org/project/pywin32-ctypes/ | Ctypes-based access to Windows Credential Vault without native C compilation requirements. |

---

## 3. Build & Packaging Dependencies

| Package | SPDX License Identifier | License Name | Upstream URL | Purpose & Compliance Note |
|---|---|---|---|---|
| **PyInstaller** | GPL-2.0-or-later WITH Bootloader-exception | GNU General Public License v2 or later with Bootloader Exception | https://www.pyinstaller.org/ | Creation of standalone Windows binary executables. Output executables are permitted for distribution without GPL viral contagion under the PyInstaller Bootloader Special Exception. |
| **pyinstaller-hooks-contrib** | Apache-2.0 | Apache License 2.0 | https://github.com/pyinstaller/pyinstaller-hooks-contrib | Community packaging hooks for third-party libraries. |
| **altgraph** | MIT | MIT License | https://pypi.org/project/altgraph/ | Dependency graph analysis for PyInstaller packaging. |
| **packaging** | Apache-2.0 OR BSD-2-Clause | Apache-2.0 or BSD-2-Clause | https://pypi.org/project/packaging/ | PEP 440 version parsing and Python package metadata parsing. |

---

## 4. Development, Quality Assurance & Contract Test Dependencies

| Package | SPDX License Identifier | License Name | Upstream URL | Purpose & Security Baseline |
|---|---|---|---|---|
| **pytest** | MIT | MIT License | https://pytest.org/ | Automated contract and unit test suite runner. Enforces >=9.1.1 floor against CVE-2025-7117 / GHSA-6w46-j5rx-g56g. |
| **pluggy** | MIT | MIT License | https://pypi.org/project/pluggy/ | Plugin and hook management for pytest. |
| **iniconfig** | MIT | MIT License | https://pypi.org/project/iniconfig/ | Fast INI configuration file parsing for pytest configuration. |
| **ruff** | MIT OR Apache-2.0 | MIT or Apache-2.0 | https://astral.sh/ruff | Ultra-fast Python linter and code style enforcement (>=0.9.0). |

---

## 5. Standard Library & OS Components

- **Python Standard Library:** Licensed under PSFL-2.0 (Python Software Foundation License). Includes 	kinter, xml.etree.ElementTree, json, subprocess, pathlib, hashlib, logging, and os.
- **Windows SDK Components (makeappx.exe, signtool.exe):** Copyright © Microsoft Corporation. Provided under the Microsoft Windows SDK EULA. Tools are invoked as external unprivileged sub-processes and are not redistributed with WinStorePackager source code.

---

## 6. Governance & Compliance Invariants

1. **No Copyleft Contagion:** All runtime and transitive libraries are licensed under permissive licenses (HPND-sell-variant, MIT, BSD-3-Clause, Apache-2.0). PyInstaller's build output is covered by the official Bootloader Exception.
2. **Deterministic Vulnerability Floors:** All dependencies strictly enforce minimum version floors in 
equirements.txt and pyproject.toml to guard against historical CVEs.
3. **Fail-Closed Verification:** Automated test suite (	ests/test_security_license_contract.py and 	ests/test_metadata.py) asserts license and dependency constraints on every test run.
