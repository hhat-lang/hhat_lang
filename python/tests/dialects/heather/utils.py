from __future__ import annotations

from pathlib import Path
from typing import Callable

from hhat_lang.toolchain.project.new import (
    create_new_fn_file,
    create_new_project,
    create_new_type_file,
)

THIS_PATH = Path(__file__).parent

RawCode = str
RelativePath = Path | str


def _create_type_file(project_path: Path, file: RelativePath) -> Path:
    return create_new_type_file(project_path=project_path, file_name=file)


def _create_fn_file(project_path: Path, file: RelativePath) -> Path:
    return create_new_fn_file(project_root=project_path, file_name=file)


def _append_file(file: Path, data: str) -> None:
    with open(file, "a") as f:
        f.write(data)


def _overwrite_file(file: Path, data: str) -> None:
    with open(file, "w") as f:
        f.write(data)


def _resolve_files(
    fn: Callable[[Path, RelativePath], Path],
    project_path: Path,
    context_path: Path | str,
    data: tuple[tuple[RelativePath, RawCode], ...],
):
    for relative_path, code in data:
        full_path = project_path / context_path

        if not (full_path / (relative_path + ".hat")).exists():
            fn(project_path, relative_path)

        _append_file(full_path / (relative_path + ".hat"), code)


def start_new_project(
    name: str,
    types_files: tuple[tuple[RelativePath, RawCode], ...],
    fns_files: tuple[tuple[RelativePath, RawCode], ...],
    main_file: str,
) -> Path:
    project_path = Path(THIS_PATH / name).resolve()
    create_new_project(project_name=project_path)

    _resolve_files(_create_type_file, project_path, "src/hat_types", types_files)
    _resolve_files(_create_fn_file, project_path, "src", fns_files)
    _overwrite_file(project_path / "src" / "main.hat", main_file)

    return project_path
