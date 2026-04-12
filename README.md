<p align="center">
  <img src="https://img.shields.io/badge/Version-2.3-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge" alt="Windows">
  <img src="https://img.shields.io/badge/Target-Microsoft%20Store-orange?style=for-the-badge" alt="Microsoft Store">
</p>

<h1 align="center">WinStorePackager</h1>

<h4 align="center">GUI tool for preparing Python apps for the Microsoft Store — Manifest, Icons, and MSIX package at the click of a button</h4>

---

## Features

| Feature | Description |
|---------|-------------|
| **Manifest Generator** | Automatically creates `AppxManifest.xml` from form inputs |
| **Icon Generator** | All required Store sizes: 44×44, 50×50, 150×150, 310×310, 310×150 (Wide) |
| **Keyring Integration** | Secure storage of certificate passwords (no plaintext) |
| **Screenshot Assistant** | Captures app screenshots directly via `pygetwindow` |
| **11 Store Categories** | Predefined (Games, Productivity, Developer Tools, ...) |
| **Age Ratings** | 3+ to 18+ ratings |
| **MSIX Build** | Invokes `makeappx.exe` and `signtool.exe` from the Windows SDK |
| **Settings Persistence** | Configuration is saved in JSON and loaded on next launch |
| **Auto-Install** | Missing dependencies are automatically installed |

---

## Prerequisites

- Python 3.10+
- Windows 10/11
- [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) (for `makeappx.exe` and `signtool.exe`)
- Microsoft Store developer account (for submission)

```bash
pip install -r requirements.txt
```

---

## Installation

```bash
git clone https://github.com/lukisch/WinStorePackager.git
cd WinStorePackager
pip install -r requirements.txt
python WindowsStorePublisher_3.py
```

Or on Windows, double-click `START.bat`.

---

## Getting Started

1. **Launch the tool** — `python WindowsStorePublisher_3.py` or `START.bat`
2. **Enter app data** — Name, Publisher ID, version, path to `.py` file
3. **Select icon** — the tool automatically generates all Store sizes
4. **Generate manifest** — `AppxManifest.xml` is created
5. **Build MSIX** — Tool invokes `makeappx.exe` and creates the package
6. **Sign** — Select certificate, enter password securely via Keyring

---

## Configuration

On first launch, `settings_store_packager.json` is created (in `.gitignore` — contains personal data). Template:

```json
{
  "app_name": "MyApp",
  "publisher": "CN=YOUR-PUBLISHER-ID",
  "publisher_display": "Your Name",
  "version": "1.0.0.0",
  "makeappx_path": "C:/Program Files (x86)/Windows Kits/10/App Certification Kit/makeappx.exe",
  "signtool_path": "C:/Program Files (x86)/Windows Kits/10/App Certification Kit/signtool.exe"
}
```

You can find your Publisher ID in the [Microsoft Partner Center](https://partner.microsoft.com/dashboard).

---

## Comparison with Alternatives

| Feature | WinStorePackager | MSIX Packaging Tool | Visual Studio | Advanced Installer |
|---------|:---:|:---:|:---:|:---:|
| GUI | ✅ | ⚠️ | ✅ | ✅ |
| Python Focus | ✅ | ❌ | ❌ | ❌ |
| Auto-Icons | ✅ | ❌ | ⚠️ | ✅ |
| Manifest Template | ✅ | ❌ | ✅ | ✅ |
| Free | ✅ | ✅ | ⚠️ | ❌ |
| Screenshot Assistant | ✅ | ❌ | ❌ | ❌ |
| Keyring Security | ✅ | ❌ | ❌ | ❌ |

---

## License

Dieses Projekt steht unter der [MIT License](LICENSE).

---

## English

A GUI tool for preparing Python applications for the Microsoft Store (MSIX packaging).

### Features

- MSIX package creation
- App manifest generation
- Icon and asset management
- Store submission preparation

### Installation

```bash
git clone https://github.com/lukisch/REL-PUB_WinStorePackager.git
cd REL-PUB_WinStorePackager
pip install -r requirements.txt
python "WindowsStorePublisher_3.py"
```

### License

See [LICENSE](LICENSE) for details.

---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse aus GPL-3.0 / MIT / Apache-2.0 §§ 15–16 (je nach gewählter Lizenz).

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.

