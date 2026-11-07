# Store Listing — WinStorePackager

## Deutsch

### Kurzbeschreibung (max 100 Zeichen)
MSIX-Packaging-Tool für Python-Apps: Manifest, Icons und Store-Pakete per Klick erstellen.

### Beschreibung (max 10.000 Zeichen)
WinStorePackager ist ein GUI-Tool, das Python-Entwicklern den gesamten Prozess der Microsoft Store-Veröffentlichung abnimmt. Statt sich manuell mit AppxManifest.xml, Icon-Größen und MSIX-Build-Befehlen herumzuschlagen, erledigt WinStorePackager alles in einer übersichtlichen Oberfläche.

**Was WinStorePackager kann:**

- Manifest-Generator: Erstellt automatisch eine vollständige AppxManifest.xml aus Formular-Eingaben
- Icon-Generator: Erzeugt alle vom Store geforderten Größen (44x44, 50x50, 150x150, 310x310, 310x150 Wide) aus einem einzigen Quellbild
- MSIX-Build: Ruft makeappx.exe und signtool.exe aus dem Windows SDK auf und erstellt das fertige Paket
- Keyring-Integration: Zertifikats-Passwörter werden sicher im Windows Credential Store gespeichert — kein Klartext
- Screenshot-Assistent: Erfasst App-Screenshots direkt über pygetwindow für die Store-Einreichung
- 11 Store-Kategorien und Altersfreigaben (3+ bis 18+) vorkonfiguriert
- Einstellungen werden als JSON gespeichert und beim nächsten Start automatisch geladen

**Für wen ist WinStorePackager?**

Python-Entwickler, die ihre Desktop-Anwendungen im Microsoft Store veröffentlichen möchten, ohne sich in die Komplexität von MSIX-Packaging einzuarbeiten. Ideal für Einzelentwickler und kleine Teams.

**Voraussetzungen:**

- Python 3.10+
- Windows 10/11
- Windows SDK (für makeappx.exe und signtool.exe)
- Microsoft Store Entwicklerkonto (für die Einreichung)

**Support:**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- E-Mail: support@lukasgeiger.com
- Datenschutz und lokale Datenhaltung: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### Schlüsselwörter
MSIX, Desktop App, Manifest, Icon Generator, Entwicklertools, Paketierung, Windows App

### Kategorie
Developer Tools

---

## English

### Short Description (max 100 chars)
MSIX packaging tool for Python apps: create manifest, icons and Store packages with one click.

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

**Support:**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- Email: support@lukasgeiger.com
- Privacy and local-data boundary: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### Keywords
MSIX, Desktop App, Manifest, Icon Generator, Developer Tools, Packaging, Windows App

### Category
Developer Tools

---

## Español

### Descripción Corta (máx 100 caracteres)
Empaquetador MSIX para apps Python: crea manifiesto, iconos y paquetes Store con un clic.

### Descripción (máx 10.000 caracteres)
WinStorePackager es una herramienta gráfica que facilita todo el proceso de publicación en Microsoft Store para desarrolladores Python. En lugar de lidiar manualmente con AppxManifest.xml, tamaños de iconos y comandos de compilación MSIX, WinStorePackager centraliza todo en una interfaz clara y eficiente.

**Características principales:**

- Generador de manifiestos: genera automáticamente un AppxManifest.xml completo a partir de los datos ingresados
- Generador de iconos: produce todos los tamaños exigidos por Store (44x44, 50x50, 150x150, 310x310, 310x150 Wide) a partir de una única imagen base
- Compilación MSIX: ejecuta makeappx.exe y signtool.exe del Windows SDK para crear el paquete listo para entrega
- Integración con Credential Manager: las contraseñas de certificados se almacenan de forma segura en Windows Credential Store
- Asistente de capturas de pantalla: captura pantallas de la aplicación para Store mediante pygetwindow
- 11 categorías de Store y clasificaciones por edad (3+ a 18+) preconfiguradas
- Ajustes persistidos en JSON cargados automáticamente al iniciar

**Soporte:**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- Correo: support@lukasgeiger.com
- Política de privacidad: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### Palabras clave
MSIX, App Escritorio, Manifiesto, Generador Iconos, Herramientas Desarrollador, Empaquetado, App Windows

### Categoría
Developer Tools

---

## 简体中文

### 简短描述（最多100个字符）
Python 应用的 MSIX 打包工具：一键生成清单、图标和应用商店发布包。

### 详细描述（最多10,000个字符）
WinStorePackager 是一款图形化桌面工具，旨在为 Python 开发者简化发布到 Microsoft Store 的全流程。无需手动编写 AppxManifest.xml、切分多尺寸图标或记忆复杂的 makeappx 命令行指令，WinStorePackager 在直观统一的界面中搞定全部配置。

**核心功能：**

- 清单生成器：从表单输入自动生成结构严谨、完全合规的 AppxManifest.xml
- 图标生成器：仅需一张源图，即可批量生成所有 Store 必需图标尺寸（44x44、50x50、150x150、310x310、310x150 宽幅）
- MSIX 自动打包：调用 Windows SDK makeappx.exe 与 signtool.exe 构建并签名就绪的发布包
- 凭证安全保护：证书密码使用 Windows Credential Store 加密保护，绝不以明文存储
- 截图助手：通过 pygetwindow 快速截取正在运行的应用窗口供商店上架使用
- 预设 11 种应用分类与完整的年龄分级（3+ 至 18+）
- 所有配置以 JSON 本地持久化保存，启动时自动载入

**支持与联系：**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- 邮箱: support@lukasgeiger.com
- 隐私策略: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### 关键字
MSIX, 桌面应用, 应用清单, 图标生成器, 开发者工具, 应用打包, Windows 应用

### 类别
Developer Tools

---

## 日本語

### 簡単な説明（最大100文字）
Pythonアプリ用MSIXパッケージャー：ワンクリックでマニフェスト、アイコン、Storeパッケージを作成。

### 詳細な説明（最大10,000文字）
WinStorePackagerは、Python開発者向けにMicrosoft Store公開までの全工程を効率化するGUIデスクトップツールです。AppxManifest.xmlの手動記述やアイコンのリサイズ、複雑なMSIXビルドコマンドを覚える必要はなく、洗練されたインターフェースから一括で処理できます。

**主な機能：**

- マニフェスト自動生成：フォーム入力から完全準拠のAppxManifest.xmlを自動構築
- タイルアイコン生成：単一の高解像度画像から全Store必須サイズ（44x44、50x50、150x150、310x310、310x150 Wide）を一括出力
- MSIXビルド＆署名：Windows SDKのmakeappx.exeおよびsigntool.exeを呼び出し、署名済みパッケージを完成
- 認証情報保護：証明書パスワードはWindows資格情報ストア（Credential Store）で安全に暗号化管理
- スクリーンショット支援：pygetwindow経由で起動中のアプリ画面をStore申請用に素早くキャプチャ
- 11種類のStoreカテゴリおよび年齢レーティング（3+〜18+）を事前設定済み
- 設定内容はJSONとしてローカルに保存され次回起動時に自動復元

**サポート：**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- メール: support@lukasgeiger.com
- プライバシーポリシー: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### キーワード
MSIX, デスクトップアプリ, マニフェスト, アイコン生成, 開発ツール, パッケージング, Windowsアプリ

### カテゴリ
Developer Tools

---

## Русский

### Краткое описание (макс 100 символов)
MSIX-упаковщик для Python-приложений: манифест, иконки и пакет Store в один клик.

### Подробное описание (макс 10.000 символов)
WinStorePackager — это десктопное приложение с графическим интерфейсом, созданное для полной автоматизации подготовки и публикации Python-программ в Microsoft Store. Вместо ручного составления AppxManifest.xml, генерации десятков иконок и вызова консольных утилит сборки, WinStorePackager выполняет все операции через удобную форму.

**Ключевые возможности:**

- Генератор манифеста: автоматическое создание валидного AppxManifest.xml из параметров формы
- Построитель иконок: конвертация одного исходного изображения во все размеры для Store (44x44, 50x50, 150x150, 310x310, 310x150 Wide)
- Сборка MSIX: прозрачный вызов makeappx.exe и signtool.exe из Windows SDK для генерации готового пакета
- Безопасное хранение ключей: пароли сертификатов шифруются в диспетчере учетных данных Windows
- Ассистент скриншотов: захват окон приложения через pygetwindow для каталога Store
- 11 категорий Store и готовые возрастные рейтинги (от 3+ до 18+)
- Автоматическое сохранение конфигурации проекта в локальном JSON

**Поддержка:**

- GitHub Issues: https://github.com/file-bricks/WinStorePackager/issues
- Электронная почта: support@lukasgeiger.com
- Политика конфиденциальности: https://github.com/file-bricks/WinStorePackager/blob/master/PRIVACY_POLICY.md

### Ключевые слова
MSIX, Десктоп приложение, Манифест, Генератор иконок, Инструменты разработчика, Упаковка, Windows приложение

### Категория
Developer Tools
