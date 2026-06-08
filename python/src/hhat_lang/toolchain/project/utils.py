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


def get_update_dir(path: Path | None = None) -> Path:
    """Return the project directory to update from any reachable path.

    Prefer an ancestor with ``src/main.hat`` for regular H-hat projects. If no
    such ancestor exists, use the given/current directory as long as it looks
    like a project root with a ``src`` or ``docs`` folder. This lets ``hat
    update`` bootstrap docs for partially-created projects too.
    """
    start = (path or Path().absolute()).resolve()
    current = start if start.is_dir() else start.parent
    fallback: Path | None = None

    while current != current.parent:
        if (current / "src" / "main.hat").exists():
            return current
        if fallback is None and ((current / "src").is_dir() or (current / "docs").is_dir()):
            fallback = current
        current = current.parent

    if fallback is not None:
        return fallback

    raise ValueError("Not inside a H-hat project directory or src/docs folder missing")
