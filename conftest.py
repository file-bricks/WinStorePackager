from __future__ import annotations


def pytest_configure(config) -> None:
    """Anchor default basetemp inside the repository root instead of the caller CWD."""
    if config.option.basetemp is None:
        config.option.basetemp = str(config.rootpath / ".pytest_temp")
