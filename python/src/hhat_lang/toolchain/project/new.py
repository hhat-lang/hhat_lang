"""When using `hat new` on terminal, should call this file"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhat_lang.toolchain.project.utils import str_to_path


def _is_project_scope(project_name: str | Path, some_path: Path) -> bool:
    project_name = str_to_path(project_name)

    if some_path.is_relative_to(project_name):
        return True

    return False


######################
# CREATE NEW PROJECT #
######################


def create_new_project(project_name: str | Path) -> Any:
    project_name = str_to_path(project_name)

    _create_template_folders(project_name)
    _create_template_files(project_name)


def _create_template_folders(project_name: Path) -> Any:
    # create root folder 'project_name' name
    os.mkdir(project_name)

    # create project template structure
    os.mkdir(project_name / "src")
    os.mkdir(project_name / "src" / "hat_types")
    os.mkdir(project_name / "src" / "hat_docs")
    os.mkdir(project_name / "src" / "hat_docs" / "hat_types")
    os.mkdir(project_name / "tests")
    # os.mkdir(project_name / "proofs")  # TODO: once proofs are incorporated, include them


def _create_template_files(project_name: Path) -> Any:
    open(project_name / "src" / "main.hat", "w").close()
    open(project_name / "src" / "hat_docs" / "main.hat.md", "w").close()


###################
# CREATE NEW FILE #
###################


def create_new_file(project_name: str | Path, file_name: str | Path) -> Any:
    """Create a new ``.hat`` source file and mirrored documentation file.

    If ``file_name`` is not under ``src/`` it is placed there automatically.
    Documentation is written to ``src/hat_docs/`` mirroring the source path,
    and the ``.hat`` extension is appended if missing.
    """

    project_name = str_to_path(project_name)
    if not project_name.is_dir():
        raise FileNotFoundError(f"Project directory '{project_name}' not found.")

    file_path = Path(file_name)
    # ensure the file has a `.hat` extension
    if file_path.suffix != ".hat":
        file_path = file_path.with_suffix(file_path.suffix + ".hat")

    source_full_path = (
        (project_name / file_path).resolve()
        if not file_path.is_absolute()
        else file_path.resolve()
    )

    if not _is_project_scope(project_name, source_full_path):
        raise ValueError("The target file path is outside the project directory.")

    rel_path = source_full_path.relative_to(project_name)
    if rel_path.parts[:1] != ("src",):
        rel_path = Path("src") / rel_path
        source_full_path = project_name / rel_path

    docs_rel = rel_path.relative_to("src").with_suffix(rel_path.suffix + ".md")
    docs_full_path = project_name / "src" / "hat_docs" / docs_rel

    source_full_path.parent.mkdir(parents=True, exist_ok=True)
    docs_full_path.parent.mkdir(parents=True, exist_ok=True)

    if source_full_path.exists() or docs_full_path.exists():
        raise FileExistsError(f"File {source_full_path} or its docs already exists")

    try:
        open(source_full_path, "x").close()
        open(docs_full_path, "x").close()
    except OSError as exc:
        raise OSError(f"Could not create new file: {exc}")


def create_new_type_file(project_name: str | Path, file_name: str | Path) -> Any:
    """Create a new ``.hat`` type file and mirrored documentation.

    The type source is placed under ``src/hat_types`` (if not already), and
    documentation is written under ``src/hat_docs/hat_types`` mirroring the
    relative path.  The ``.hat`` extension is appended if missing.
    """

    project_name = str_to_path(project_name)
    if not project_name.is_dir():
        raise FileNotFoundError(f"Project directory '{project_name}' not found.")

    file_path = Path(file_name)

    # Check the original path first to avoid paths like "../bad"
    pre_full = (
        (project_name / file_path).resolve()
        if not file_path.is_absolute()
        else file_path.resolve()
    )

    if not _is_project_scope(project_name, pre_full):
        raise ValueError("The target file path is outside the project directory.")

    if not file_path.is_absolute():
        if file_path.parts[:2] == ("src", "hat_types"):
            pass
        else:
            if file_path.parts[:1] == ("src",):
                file_path = Path(*file_path.parts[1:])
            file_path = Path("src") / "hat_types" / file_path

    if file_path.suffix != ".hat":
        file_path = file_path.with_suffix(".hat")

    source_full_path = (
        (project_name / file_path).resolve()
        if not file_path.is_absolute()
        else file_path.resolve()
    )

    rel_path = source_full_path.relative_to(project_name)
    if rel_path.parts[:2] != ("src", "hat_types"):
        rel_path = Path("src") / "hat_types" / rel_path
        source_full_path = project_name / rel_path

    docs_rel = rel_path.relative_to("src").with_suffix(rel_path.suffix + ".md")
    docs_full_path = project_name / "src" / "hat_docs" / docs_rel

    source_full_path.parent.mkdir(parents=True, exist_ok=True)
    docs_full_path.parent.mkdir(parents=True, exist_ok=True)

    if source_full_path.exists() or docs_full_path.exists():
        raise FileExistsError(
            f"Type file {source_full_path} or its docs already exists"
        )

    try:
        open(source_full_path, "x").close()
        open(docs_full_path, "x").close()
    except OSError as exc:
        raise OSError(f"Could not create new type file: {exc}")
