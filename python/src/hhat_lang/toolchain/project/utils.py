from __future__ import annotations

from pathlib import Path


def str_to_path(obj: str | Path) -> Path:
    return obj if isinstance(obj, Path) else Path(obj).resolve()


def get_proj_dir(path: Path | None = None) -> Path:
    current = path or Path().absolute()
    while current != current.parent:
        if (current / "src" / "main.hat").exists():
            return current
        current = current.parent
    raise ValueError("Not inside a H-hat project directory or src/main.hat missing")
