# Projektprofilformat `winstorepackager-project-v1`

Dieses JSON-Format ist der gemeinsame, plattformneutrale Kontrakt für den
Projektprofil-Import/-Export der Windows-Desktop-App und die SDK-freie
Profilprüfung. Das Schema bleibt absichtlich frei von Windows-spezifischen
Geheimnissen und von einer bestimmten Client-Oberfläche.

Ein früherer lokaler `web_companion/` wurde mit Commit `05705f9` entfernt. Das
Repository liefert daher aktuell keinen Web-Companion; externe Werkzeuge können
das dokumentierte JSON-Schema unabhängig davon verarbeiten.

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

Import und Export validieren diesen Vertrag strikt. Unbekannte Felder und
falsche Feldtypen werden als Schema-Drift gemeldet, statt stillschweigend
übernommen zu werden. Auch in ansonsten erlaubten Feldern lehnt der Validator
echte Publisher-CNs, exakte Windows-SDK-Toolpfade, Zertifikatsdateien
(`.pfx`/`.p12`) sowie erkennbare Zugangstoken und private Schlüssel ab. Diese
Werte werden erst nach dem Import in den hostlokalen Einstellungen ergänzt.
`null` wird bei optionalen Feldern wie ein fehlender Wert behandelt; insbesondere
bleibt `enable_i18n` dann beim sicheren Standard `true`. Frühere Profile mit
nicht dokumentierten Erweiterungsfeldern müssen diese Felder vor dem Import
entfernen oder in ein neues, versioniertes Schema migrieren.

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

## Desktop-/Offline-Workflow

1. Desktop-App: Profil exportieren
2. JSON optional mit einem externen, schema-kompatiblen Werkzeug bearbeiten oder
   mit `unix_preflight.py` prüfen
3. Desktop-App: Profil importieren und Windows-spezifische Felder lokal ergänzen
