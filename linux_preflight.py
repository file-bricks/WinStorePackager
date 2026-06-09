from __future__ import annotations

import sys
import warnings
from pathlib import Path
from typing import Any

from unix_preflight import run_unix_preflight, format_report, main


def run_linux_preflight(
    project_root: str | Path,
    *,
    profile_path: str | Path | None = None,
) -> dict[str, Any]:
    warnings.warn(
        "run_linux_preflight is deprecated, use run_unix_preflight instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    res = run_unix_preflight(project_root, profile_path=profile_path)
    res["platform"] = "linux"
    return res


if __name__ == "__main__":
    print(
        "WARNING: linux_preflight.py is deprecated and has been generalized to unix_preflight.py.",
        file=sys.stderr,
    )
    raise SystemExit(main())
