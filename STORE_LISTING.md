# Store Listing — WinStorePackager

## Deutsch

### Kurzbeschreibung (max 100 Zeichen)
MSIX-Packaging-Tool fuer Python-Apps — Manifest, Icons und Store-Paket per Klick erstellen.

### Beschreibung (max 10.000 Zeichen)
WinStorePackager ist ein GUI-Tool, das Python-Entwicklern den gesamten Prozess der Microsoft Store-Veroeffentlichung abnimmt. Statt sich manuell mit AppxManifest.xml, Icon-Groessen und MSIX-Build-Befehlen herumzuschlagen, erledigt WinStorePackager alles in einer uebersichtlichen Oberflaeche.

**Was WinStorePackager kann:**

- Manifest-Generator: Erstellt automatisch eine vollstaendige AppxManifest.xml aus Formular-Eingaben
- Icon-Generator: Erzeugt alle vom Store geforderten Groessen (44x44, 50x50, 150x150, 310x310, 310x150 Wide) aus einem einzigen Quellbild
- MSIX-Build: Ruft makeappx.exe und signtool.exe aus dem Windows SDK auf und erstellt das fertige Paket
- Keyring-Integration: Zertifikats-Passwoerter werden sicher im Windows Credential Store gespeichert — kein Klartext
- Screenshot-Assistent: Erfasst App-Screenshots direkt ueber pygetwindow fuer die Store-Einreichung
- 11 Store-Kategorien und Altersfreigaben (3+ bis 18+) vorkonfiguriert
- Einstellungen werden als JSON gespeichert und beim naechsten Start automatisch geladen

**Fuer wen ist WinStorePackager?**

Python-Entwickler, die ihre Desktop-Anwendungen im Microsoft Store veroeffentlichen moechten, ohne sich in die Komplexitaet von MSIX-Packaging einzuarbeiten. Ideal fuer Einzelentwickler und kleine Teams.

**Voraussetzungen:**

- Python 3.10+
- Windows 10/11
- Windows SDK (fuer makeappx.exe und signtool.exe)
- Microsoft Store Entwicklerkonto (fuer die Einreichung)

### Schluesselwoerter
MSIX, Python, Packaging, Microsoft Store, App-Veroeffentlichung, Manifest, Icon-Generator, Entwickler-Tool, Windows SDK, Store-Einreichung

### Kategorie
Developer Tools

---

## English

### Short Description (max 100 chars)
MSIX packaging tool for Python apps — create manifest, icons and Store package with one click.

### Description (max 10,000 chars)
WinStorePackager is a GUI tool that handles the entire Microsoft Store publishing process for Python developers. Instead of manually dealing with AppxManifest.xml, icon sizes, and MSIX build commands, WinStorePackager does everything in a clean, intuitive interface.

**What WinStorePackager does:**

- Manifest Generator: Automatically creates a complete AppxManifest.xml from form inputs
- Icon Generator: Produces all Store-required sizes (44x44, 50x50, 150x150, 310x310, 310x150 Wide) from a single source image
- MSIX Build: Invokes makeappx.exe and signtool.exe from the Windows SDK to create the final package
- Keyring Integration: Certificate passwords are stored securely in the Windows Credential Store — no plaintext
- Screenshot Assistant: Captures app screenshots directly via pygetwindow for Store submission
- 11 Store categories and age ratings (3+ to 18+) preconfigured
- Settings are saved as JSON and automatically loaded on next launch

**Who is WinStorePackager for?**

Python developers who want to publish their desktop applications on the Microsoft Store without diving into the complexity of MSIX packaging. Ideal for solo developers and small teams.

**Requirements:**

- Python 3.10+
- Windows 10/11
- Windows SDK (for makeappx.exe and signtool.exe)
- Microsoft Store developer account (for submission)

### Keywords
MSIX, Python, packaging, Microsoft Store, app publishing, manifest, icon generator, developer tool, Windows SDK, Store submission

### Category
Developer Tools
