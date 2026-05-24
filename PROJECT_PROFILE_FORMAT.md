# Projektprofilformat `winstorepackager-project-v1`

Dieses JSON-Format ist der gemeinsame Kontrakt zwischen der Windows-Desktop-App und dem Web-Companion von WinStorePackager.

## Ziel

- Projektmetadaten plattformübergreifend vorbereiten
- Store-Listing-Texte, Pfade und Manifest-relevante Felder austauschbar halten
- sensible Werte bewusst lokal halten

## Enthalten

- App-Name, Identity Name, Publisher Display Name, Version
- Pfade für Skript, Icon, Source, Installer, Ausgabeordner und EXE-Name
- Privacy Policy, Support-URL, Kategorie, Altersfreigabe, Capabilities
- Beschreibung, Changelog, README
- Lizenzdateien und zusätzliche Lizenztexte
- `enable_i18n`

## Nicht enthalten

- echte Publisher-ID (`CN=...`)
- Windows-SDK-Pfade (`makeappx.exe`, `signtool.exe`, `appcert.exe`)
- Python-Buildpfad
- Zertifikatspfad und Zertifikatspasswort
- Keyring-Inhalte

## Struktur

```json
{
  "format": "winstorepackager-project-v1",
  "schema_version": 1,
  "project_root": ".",
  "metadata": {
    "app_name": "MeineApp",
    "publisher_display": "Mein Studio",
    "identity_name": "MeineApp.Desktop",
    "version": "1.0.0.0"
  },
  "paths": {
    "script_path": "src/main.py",
    "icon_path": "assets/icon.png",
    "source_path": "dist/source.zip",
    "installer_path": "dist/MeineApp.exe",
    "output_dir": "releases/store",
    "exe_name": "MeineApp.exe"
  },
  "store": {
    "privacy_url": "https://example.com/privacy",
    "support_url": "https://example.com/support",
    "capabilities": ["internetClient"],
    "category": "Developer Tools",
    "age_rating": "3+",
    "description": "Kurzbeschreibung",
    "changelog": "Version 1.0.0.0\n- Erstes Release"
  },
  "documents": {
    "readme": "README-Inhalt",
    "license_files": ["LICENSE.txt"],
    "license_text_entries": ["MIT License"]
  },
  "settings": {
    "enable_i18n": true
  }
}
```

## Auflösung relativer Pfade

- Die Desktop-App speichert Pfade nach Möglichkeit relativ zur erkannten Projektwurzel.
- Beim Import werden relative Pfade gegen `project_root` aufgelöst.
- Falls `project_root` relativ ist, wird es relativ zum Speicherort der JSON-Datei interpretiert.

## Companion-Workflow

1. Desktop-App: Profil exportieren
2. Web-Companion: JSON lokal laden und weiter bearbeiten
3. Web-Companion: JSON wieder exportieren
4. Desktop-App: Profil importieren und Windows-spezifische Felder lokal ergänzen
