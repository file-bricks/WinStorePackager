import subprocess
import sys

import WindowsStorePublisher_3 as wsp


class _Value:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def test_license_collection_never_installs_packages_at_runtime(tmp_path, monkeypatch):
    app = wsp.StorePackagerApp.__new__(wsp.StorePackagerApp)
    app.script_path = _Value(str(tmp_path / "app.py"))
    app.get_build_interpreter = lambda: sys.executable
    calls = []

    def unavailable_tool(command, **kwargs):
        calls.append(command)
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(wsp.subprocess, "run", unavailable_tool)

    success, message = app.collect_python_licenses(tmp_path)

    assert success is False
    assert "kontrollierten Build-Umgebung" in message
    assert calls == [[sys.executable, "-m", "pip_licenses", "--with-license-file", "--format=plain"]]
    assert not (tmp_path / "THIRD_PARTY_LICENSES.txt").exists()
