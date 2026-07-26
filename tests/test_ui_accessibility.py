import sys
import tkinter as tk
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import WindowsStorePublisher_3 as _wsp


def _minimal_app() -> "_wsp.StorePackagerApp":
    app = _wsp.StorePackagerApp.__new__(_wsp.StorePackagerApp)
    tk.Tk.__init__(app)
    app.withdraw()

    app.app_name = tk.StringVar(value="TestApp")
    app.publisher = tk.StringVar(value="CN=Test")
    app.publisher_display = tk.StringVar(value="Test Studio")
    app.identity_name = tk.StringVar(value="Test.TestApp")
    app.version = tk.StringVar(value="1.0.0.0")
    app.script_path = tk.StringVar()
    app.icon_path = tk.StringVar()
    app.source_path = tk.StringVar()
    app.installer_path = tk.StringVar()
    app.output_dir = tk.StringVar(value="store_package")
    app.exe_name = tk.StringVar(value="TestApp.exe")
    app.makeappx_path = tk.StringVar()
    app.signtool_path = tk.StringVar()
    app.appcert_path = tk.StringVar()
    app.pfx_path = tk.StringVar()
    app.pfx_password = tk.StringVar()
    app.timestamp_url = tk.StringVar(value="http://timestamp.example")
    app.msix_name = tk.StringVar(value="TestApp.msix")
    app.python_path = tk.StringVar()
    app.enable_i18n = tk.BooleanVar(value=False)
    return app


def _button_texts(parent: tk.Misc) -> list[str]:
    texts: list[str] = []
    stack = [parent]
    while stack:
        widget = stack.pop()
        for child in widget.winfo_children():
            stack.append(child)
            try:
                if child.winfo_class() == "TButton":
                    texts.append(child.cget("text"))
            except tk.TclError:
                continue
    return texts


class TestUiAccessibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = _minimal_app()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_metadata_tab_uses_contextual_button_labels(self):
        parent = tk.Frame(self.app)
        self.app.build_metadata_tab(parent)
        texts = _button_texts(parent)

        for label in (
            "Skript wählen",
            "Icon wählen",
            "Quelle wählen",
            "Installer wählen",
            "README laden",
            "Beschreibung laden",
        ):
            self.assertIn(label, texts)

        self.assertNotIn("Wählen", texts)
        self.assertNotIn("Datei laden", texts)

    def test_build_tab_uses_contextual_button_labels(self):
        parent = tk.Frame(self.app)
        self.app.build_build_tab(parent)
        texts = _button_texts(parent)

        for label in (
            "Python wählen",
            "MakeAppx wählen",
            "SignTool wählen",
            "AppCert wählen",
            "Zertifikat wählen",
        ):
            self.assertIn(label, texts)

        self.assertNotIn("Wählen", texts)


if __name__ == "__main__":
    unittest.main()
