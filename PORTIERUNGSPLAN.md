# Portierungsplan - WinStorePackager

Stand: 2026-05-24

## Kurzentscheidung

WinStorePackager bleibt primär eine Windows-Desktop-App, weil der Kernnutzen direkt an Microsoft Store, MSIX, Windows SDK, `makeappx.exe`, `signtool.exe`, Zertifikate und WACK-Tests gebunden ist. Plattformübergreifende Nutzung ist trotzdem sinnvoll, aber als Companion- und Vorbereitungsfluss: Web/PWA, macOS und Linux sollen Projektmetadaten, Manifest-Entwürfe, Icon-Checks und Paket-Readiness vorbereiten können; der finale MSIX-Build bleibt Windows.

## Warum Plattformplanung sinnvoll ist

- Nachfrage: Zielgruppe sind Python-Entwickler und kleine Teams, die oft auf mehreren Systemen arbeiten, auch wenn die finale Store-Einreichung Windows braucht.
- Mobilität: Ein Web/PWA-Companion kann Store-Listing, App-Metadaten und Checklisten unterwegs vorbereiten.
- Usecases: Vorabprüfung von Projektstruktur, Icon-Größen, Store-Kategorie, Altersfreigabe, Datenschutz- und Release-Texten braucht nicht zwingend Windows SDK.
- Qualität: Ein gemeinsames Austauschformat verhindert, dass Web-/Mac-/Linux-Vorarbeit vom Windows-Packaging abweicht.

## Plattformoptionen

| Option | Bewertung | Entscheidung |
|---|---|---|
| Windows Store Release | Sehr sinnvoll. Das Tool dogfoodet seine eigene Zielplattform und ist in der Pipeline Priorität I. | P0, Hauptkanal. |
| Android-Version oder Android-Clone | Niedriger Nutzen als native App, weil MSIX-Build und Code-Signing dort nicht möglich sind. | Kein nativer Clone; nur PWA-Nutzung für Listing-/Checklistenarbeit. |
| Webapp | Sinnvoll als Companion: Projektfragebogen, Manifest-Entwurf, Store-Listing-Builder, Icon-Check, Export. | P1, bevorzugte plattformübergreifende Linie. |
| iOS-Version | Wie Android: native App bringt wenig, PWA reicht für mobile Vorbereitung. | P2 als PWA-Testziel, keine native App. |
| Mac App | Mittel: Mac-Entwickler können Python-Projekte vorbereiten, aber nicht final signieren und packen. | P2/P3 als begrenzter Preflight-Helper oder PWA-Nutzung. |
| Linux-Version | Mittel: Für Python-Entwickler relevant, aber finaler MSIX-Build bleibt Windows. | P2/P3 als CLI-/Preflight-Helper oder PWA-Nutzung. |

## Zielarchitektur

1. Windows-Desktop-App bleibt die Referenz für finalen MSIX-Build, Signierung, Screenshot-Erfassung und WACK-Vorbereitung.
2. Gemeinsames Austauschformat `winstorepackager-project-v1.json` enthält App-Metadaten, Publisher-Platzhalter, Version, Icons, Store-Kategorie, Altersfreigabe, Listing-Texte und Pfade als relative Projektverweise.
3. Web/PWA-Companion erzeugt und validiert dieses Format, ohne Zertifikate oder lokale Projektdateien hochzuladen.
4. macOS/Linux-Preflight ist optional und auf SDK-unabhängige Prüfungen begrenzt: Python-Projektstruktur, vorhandene Icons, README/Privacy/Store-Listing, Versionsschema.
5. Android/iOS nutzen die Web/PWA-Linie statt nativer Entwicklung.

## Export- und Importlinie

Der Desktop soll `winstorepackager-project-v1.json` exportieren und importieren können. Das Format ist der Brückenkontrakt zwischen Desktop, Web/PWA und optionalen Preflight-Tools. Sensible Werte wie echte Publisher-ID, Zertifikatspfade und Zertifikatspasswörter dürfen nicht exportiert werden; sie bleiben lokale Windows-Einstellungen.

## Umsetzungsstatus

- Bestehende Planung vor diesem Check: keine eigene `PORTIERUNGSPLAN.md` gefunden.
- Windows-Desktop-App: vorhanden, Store-Pipeline-Eintrag aktiv.
- Web/PWA: noch nicht angelegt.
- Android/iOS: keine native Planung, PWA-Testziel offen.
- macOS/Linux: nur Fehlermeldungs-/Preflight-Spuren im Code, keine belastbare Produktlinie.
- Austauschformat: noch offen.

## Nächste Schritte

1. `winstorepackager-project-v1.json` als Schema dokumentieren und einen Export/Import-Smoke-Test ergänzen.
2. Desktop-App um Export/Import der Projektmetadaten erweitern.
3. Web/PWA-Companion als statischen Fragebogen mit lokalem JSON-Export planen.
4. macOS-/Linux-Preflight bewusst auf SDK-freie Checks begrenzen.
5. Store-Dogfooding abschließen: WinStorePackager mit WinStorePackager paketieren, Screenshots und Store-Listing finalisieren.
