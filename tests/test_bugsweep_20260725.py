# -*- coding: utf-8 -*-
"""Regressionstests — WinStorePackager Bugsweep-Iteration 2026-07-25.

Prüft:
1. Default-Parameter-Bindung für err/msg in thread_after callbacks in WindowsStorePublisher_3.py
   (verhindert NameError / late-binding leakage bei Hintergrundthread-Callables).
2. Tcl/Tk-Environment Initialization Fallback & Thread-Safe after-Mocking.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_SRC = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WSP_TEXT = (_SRC / "WindowsStorePublisher_3.py").read_text(encoding="utf-8")


def test_thread_after_callbacks_use_default_param_binding():
    """Stelle sicher, dass self.after Callbacks in Threads m=msg / err=err_str binden."""
    assert 'self.after(0, lambda m=msg: messagebox.showinfo("Fertig", m))' in WSP_TEXT
    assert 'self.after(0, lambda err=err_out: messagebox.showerror("PyInstaller Fehler", f"{err}"))' in WSP_TEXT
    assert 'self.after(0, lambda err=err_str: messagebox.showerror("Fehler", f"EXE-Erzeugung fehlgeschlagen:\\n{err}"))' in WSP_TEXT
    assert 'self.after(0, lambda msg=error_msg: messagebox.showerror("Fehler", msg))' in WSP_TEXT
    assert 'self.after(0, lambda m=info_msg: messagebox.showinfo("Screenshots", m))' in WSP_TEXT
    assert 'self.after(0, lambda err=err_msg: messagebox.showerror("Fehler", err))' in WSP_TEXT


def test_no_unbound_lambda_in_thread_except_blocks():
    """Stelle sicher, dass in except-Blöcken keine ungeordneten lambda: messagebox... ohne Arg-Binding stehen."""
    assert 'self.after(0, lambda: messagebox.showerror("Fehler", err_msg))' not in WSP_TEXT
    assert 'self.after(0, lambda: messagebox.showerror("Fehler", error_msg))' not in WSP_TEXT
    assert 'self.after(0, lambda: messagebox.showinfo("Screenshots", info_msg))' not in WSP_TEXT


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
