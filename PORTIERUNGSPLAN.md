# Portierungsplan - WinStorePackager

Stand: 2026-05-28

## Kurzentscheidung

WinStorePackager bleibt primär eine Windows-Desktop-App, weil der Kernnutzen direkt an Microsoft Store, MSIX, Windows SDK, `makeappx.exe`, `signtool.exe`, Zertifikate und WACK-Tests gebunden ist. Plattformübergreifende Nutzung ist trotzdem sinnvoll, aber als Companion- und Vorbereitungsfluss: Web/PWA, macOS und Linux sollen Projektmetadaten, Manifest-Entwürfe, Icon-Checks und Paket-Readiness vorbereiten können; der finale MSIX-Build bleibt Windows.

## Warum Plattformplanung sinnvoll ist

- Nachfrage: Zielgruppe sind Python-Entwickler und kleine Teams, die oft auf mehreren Systemen arbeiten, auch wenn die finale Store-Einreichung Windows braucht.
- Mobilität: Ein Web/PWA-Companion kann Store-Listing, App-Metadaten und Checklisten unterwegs vorbereiten.
- Usecases: Vorabprüfung von Projektstruktur, Icon-Größen, Store-Kategorie, Altersfreigabe, Datenschutz- und Release-Texten braucht nicht zwingend Windows SDK.
- Qualität: Ein gemeinsames Austauschformat verhindert, dass Web-/Mac-/Linux-Vorarbeit vom Windows-Packaging abweicht.

## Feature- und Usecase-Ableitung

### Beste Feature-Version

- Windows-Desktop-App erzeugt Manifest, Store-Assets, Screenshots, MSIX-Paket, Signaturvorbereitung und WACK-Vorbereitung aus lokalen Projektdaten.
- Projektprofil-Import/-Export hält Store-Metadaten, Pfade, Capabilities, Listing-Texte und Dokumenthinweise in `winstorepackager-project-v1.json` zusammen.
- Web/PWA-Companion bietet Projektfragebogen, Manifest-Vorschau, Icon-Check, Offline-Shell und lokalen Profilimport/-export ohne Upload sensibler Daten.
- macOS-/Linux-Preflight kann nur SDK-freie Checks leisten: Struktur, Version, Icon, README, Privacy Policy, Support-URL und Store-Listing.

### Usecase-Settings

| Setting | Nutzer | Usecases | Konsequenz |
|---|---|---|---|
| Windows-Packager | Entwickler, die ein Python-Projekt tatsächlich für den Microsoft Store bauen | Manifest erzeugen, Assets generieren, MSIX bauen, signieren, WACK vorbereiten, Dogfooding durchführen | Eigenständige Windows-Desktop-App bleibt Hauptprodukt. |
| Cross-Platform-Preflight | Entwickler oder Teammitglieder auf Web, macOS oder Linux | Projektdaten erfassen, Store-Texte abstimmen, Icons prüfen, Readiness bewerten, Profil exportieren | Companion/Preflight statt eigenständiger Plattform-App. |
| Mobile-Review | Entwickler unterwegs oder nichttechnische Mitwirkende | Listing-Texte, Kategorie, Datenschutz-/Support-Links und Checklisten prüfen | PWA reicht; native Android-/iOS-App ist kein eigener Usecase. |

Damit fallen Windows und Companion nicht in dasselbe Usecase-Setting: Windows erfüllt den finalen Build-Usecase, der Companion sammelt und validiert Zuarbeit für diesen Build. Die Verbindung zur Hauptapp ist selbst ein Usecase, daher bleibt der Web/PWA-Teil ein Companion.

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

Der Desktop kann `winstorepackager-project-v1.json` exportieren und importieren. Das Format ist der Brückenkontrakt zwischen Desktop, Web/PWA und optionalen Preflight-Tools. Sensible Werte wie echte Publisher-ID, Zertifikatspfade und Zertifikatspasswörter dürfen nicht exportiert werden; sie bleiben lokale Windows-Einstellungen.

## Umsetzungsstatus

- Pfad-A-Review 2026-05-28: vorhandener Plan bestätigt; ergänzt wurden Feature-zu-Usecase-Ableitung, getrennte Usecase-Settings und klarere Abgrenzung zwischen Hauptapp und Companion.
- Windows-Desktop-App: vorhanden, Store-Pipeline-Eintrag aktiv.
- Windows-Dogfooding: EXE-/Startskript-Stand wurde am 2026-05-26 vorbereitet; offen bleiben echtes Self-Packaging als MSIX, Store-Screenshot-Set und WACK-Protokoll.
- Web/PWA: Companion unter `web_companion/` ist jetzt als installierbare lokale PWA ausgebaut. Er bearbeitet lokale Projektprofile, zeigt Manifest-Vorschau, prüft Icon-Größe, exportiert/importiert `winstorepackager-project-v1.json` und bringt Service Worker, Offline-Seite, Install-Status sowie `serve_companion.py` für `localhost` mit.
- Android/iOS: keine native Planung, PWA-Testziel offen.
- macOS/Linux: nur Fehlermeldungs-/Preflight-Spuren im Code, keine belastbare Produktlinie.
- Austauschformat: als `winstorepackager-project-v1.json` dokumentiert und in Desktop-App + Web-Companion verdrahtet.

## Nächste Schritte

1. Windows-Dogfooding abschließen: eigenes Projektprofil laden, WinStorePackager als MSIX paketieren, Store-Screenshots erzeugen und WACK-Protokoll ablegen.
2. Web-Companion auf Android Chrome und iOS Safari als PWA-Testziel prüfen.
3. Optionalen Listing-Builder für DE/EN-Texte im Companion vertiefen.
4. macOS-/Linux-Preflight bewusst auf SDK-freie Checks begrenzen.
5. Keine native Mobile-App starten, solange kein eigenständiger Mobile-Usecase jenseits von Review und Zuarbeit entsteht.
