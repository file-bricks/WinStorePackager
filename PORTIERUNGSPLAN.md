# Portierungsplan - WinStorePackager

Stand: 2026-05-28

## Kurzentscheidung

WinStorePackager braucht nur Desktop-Apps. Der Kernnutzen hängt an Microsoft Store, MSIX, Windows SDK, `makeappx.exe`, `signtool.exe`, Zertifikaten und WACK-Tests. Eine Web/PWA-, Android- oder iOS-Linie ist unnötig und wird nicht weiter geplant.

Die sinnvolle Portierungslinie ist deshalb:

1. Windows-Desktop als Hauptprodukt und Dogfooding-Ziel.
2. macOS-Desktop nur als optionaler SDK-freier Preflight-Smoke für Projektstruktur, Metadaten und Dokumente.
3. Linux-Desktop nur als optionaler SDK-freier Preflight-Smoke für Projektstruktur, Metadaten und Dokumente.

Der finale MSIX-Build, Signierung, Store-Screenshot-Erstellung und WACK bleiben Windows-only.

## Warum Plattformplanung trotzdem sinnvoll ist

- Nachfrage: Zielgruppe sind Python-Entwickler, die am Ende ein Windows-Store-Paket bauen wollen.
- Desktop-Realität: Die relevanten Werkzeuge, Zertifikate und Tests laufen lokal auf Desktop-Systemen, nicht auf Mobilgeräten.
- Qualität: macOS-/Linux-Smokes können früh zeigen, ob Projektprofile, README, Store-Listing und Icons formal plausibel sind, ohne einen eigenen Store-Build zu versprechen.
- Abgrenzung: Mobile und Web würden keinen eigenständigen Kernusecase erfüllen, sondern nur eine zweite Oberfläche für dieselben Desktop-Daten schaffen.

## Feature- und Usecase-Ableitung

### Beste Feature-Version

- Windows-Desktop-App erzeugt Manifest, Store-Assets, Screenshots, MSIX-Paket, Signaturvorbereitung und WACK-Vorbereitung aus lokalen Projektdaten.
- Projektprofil-Import/-Export hält Store-Metadaten, Pfade, Capabilities, Listing-Texte und Dokumenthinweise in `winstorepackager-project-v1.json` zusammen.
- macOS-/Linux-Preflight prüft nur SDK-freie Punkte: Projektstruktur, Version, Icon, README, Privacy Policy, Support-URL und Store-Listing.

### Usecase-Settings

| Setting | Nutzer | Usecases | Konsequenz |
|---|---|---|---|
| Windows-Packager | Entwickler, die ein Python-Projekt tatsächlich für den Microsoft Store bauen | Manifest erzeugen, Assets generieren, MSIX bauen, signieren, WACK vorbereiten, Dogfooding durchführen | Eigenständige Windows-Desktop-App bleibt Hauptprodukt. |
| Desktop-Preflight | Entwickler auf Windows, macOS oder Linux | Projektdaten prüfen, Store-Texte vorbereiten, Icons und Dokumente validieren, Profil exportieren | Desktop-Hilfsmodus oder CLI/GUI-Preflight reicht. |

Web, Android und iOS haben kein eigenes Usecase-Setting. Sie würden weder MSIX bauen noch WACK ausführen und liefern keinen Mehrwert gegenüber Desktop-Preflight.

## Plattformoptionen

| Option | Bewertung | Entscheidung |
|---|---|---|
| Windows Store Release | Sehr sinnvoll. Das Tool dogfoodet seine eigene Zielplattform und ist in der Pipeline Priorität I. | P0, Hauptkanal. |
| Windows Desktop Direct/GitHub | Sinnvoll als Entwicklerkanal und Vorstufe zur Store-Einreichung. | P0, parallel zu Store-Artefakten. |
| macOS App | Nur begrenzt sinnvoll, weil finaler MSIX-Build nicht möglich ist. | P3, optionaler SDK-freier Desktop-Preflight. |
| Linux App | Nur begrenzt sinnvoll, weil finaler MSIX-Build nicht möglich ist. | P3, optionaler SDK-freier Desktop-Preflight. |
| Webapp/PWA | Kein eigener Kernusecase. | Nicht-Ziel. |
| Android-App | Kein eigener Kernusecase. | Nicht-Ziel. |
| iOS-App | Kein eigener Kernusecase. | Nicht-Ziel. |

## Zielarchitektur

1. Windows-Desktop-App bleibt die Referenz für finalen MSIX-Build, Signierung, Screenshot-Erfassung und WACK-Vorbereitung.
2. Gemeinsames Austauschformat `winstorepackager-project-v1.json` bleibt ein Desktop-Austauschformat für Projektprofile, nicht die Grundlage für eine Web- oder Mobile-Linie.
3. macOS-/Linux-Desktop-Smokes sind optional und auf SDK-unabhängige Prüfungen begrenzt: Python-Projektstruktur, vorhandene Icons, README, Privacy Policy, Store-Listing und Versionsschema.
4. Android, iOS und Web/PWA werden nicht weiter verfolgt.

## Export- und Importlinie

Der Desktop kann `winstorepackager-project-v1.json` exportieren und importieren. Das Format ist der lokale Brückenkontrakt zwischen Windows-Hauptapp und optionalen Desktop-Preflight-Läufen. Sensible Werte wie echte Publisher-ID, Zertifikatspfade und Zertifikatspasswörter dürfen nicht exportiert werden; sie bleiben lokale Windows-Einstellungen.

## Umsetzungsstatus

- User-Korrektur 2026-05-28: Companion/Web/Mobile ist unnötig; Planung auf Desktop-only korrigiert.
- Windows-Desktop-App: vorhanden, Store-Pipeline-Eintrag aktiv.
- Windows-Dogfooding: EXE-/Startskript-Stand wurde am 2026-05-26 vorbereitet; offen bleiben echtes Self-Packaging als MSIX, Store-Screenshot-Set und WACK-Protokoll.
- macOS/Linux: nur Fehlermeldungs-/Preflight-Spuren im Code, keine belastbare Produktlinie.
- Austauschformat: als `winstorepackager-project-v1.json` dokumentiert und in der Desktop-App verdrahtet.
- Web/PWA, Android und iOS: Nicht-Ziele.

## Nächste Schritte

1. Windows-Dogfooding abschließen: eigenes Projektprofil laden, WinStorePackager als MSIX paketieren, Store-Screenshots erzeugen und WACK-Protokoll ablegen.
2. macOS-/Linux-Preflight bewusst auf SDK-freie Desktop-Checks begrenzen.
3. Bestehende Web/PWA-Companion-Hinweise bei der nächsten Doku-Hygiene entfernen oder als eingestellten Prototyp markieren.
4. Keine native Mobile- oder Webapp-Linie starten.
