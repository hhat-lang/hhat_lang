from __future__ import annotations

from pathlib import Path


def str_to_path(obj: str | Path) -> Path:
    return obj if isinstance(obj, Path) else Path(obj).resolve()
