"""When using `hat new` on terminal, should call this file"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhat_lang.toolchain.project import (
    DOCS_FOLDER_NAME,
    DOCS_TYPES_PATH,
    MAIN_DOC_FILE_NAME,
    MAIN_FILE_NAME,
    SOURCE_FOLDER_NAME,
    SOURCE_TYPES_PATH,
    IMPORTS_FOLDER_NAME,
    TESTS_FOLDER_NAME,
    IMPORTS_PATH,
)
from hhat_lang.toolchain.project.utils import str_to_path


def _is_project_scope(project_name: str | Path, some_path: Path) -> bool:
    project_name = str_to_path(project_name)

    if some_path.is_relative_to(project_name):
        return True

    return False


######################
# CREATE NEW PROJECT #
######################


def create_new_project(project_name: Path) -> Any:
    _create_template_folders(project_name)
    _create_template_files(project_name)


def _create_template_folders(project_name: Path) -> Any:
    # create root folder 'project_name' name
    os.mkdir(project_name)

    # create project template structure
    os.mkdir(project_name / SOURCE_FOLDER_NAME)
    os.mkdir(project_name / SOURCE_TYPES_PATH)
    os.mkdir(project_name / IMPORTS_PATH)
    os.mkdir(project_name / DOCS_FOLDER_NAME)
    os.mkdir(project_name / DOCS_TYPES_PATH)
    # os.mkdir(project_name / TESTS_FOLDER_NAME)  # TODO: once tests are implemented, include them
    # os.mkdir(project_name / "proofs")  # TODO: once proofs are incorporated, include them


def _create_template_files(project_name: Path) -> Any:
    with open(project_name / SOURCE_FOLDER_NAME / MAIN_FILE_NAME, "w") as f:
        f.write("main {\n\n}\n\n")

    with open(project_name / DOCS_FOLDER_NAME / MAIN_DOC_FILE_NAME, "w") as f:
        f.write(f"# {project_name.name}\n\n")


###################
# CREATE NEW FILE #
###################


def create_new_fn_file(project_root: Path, file_name: str | Path) -> Path:
    file_name = str(file_name) + ".hat"
    doc_file = file_name + ".md"
    file_path: Path = project_root / SOURCE_FOLDER_NAME / file_name

    if file_path.is_file():
        raise FileExistsError(f"File {file_path}.hat already exists")

    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    doc_path = project_root / DOCS_FOLDER_NAME / doc_file
    if doc_path.parent != Path("."):
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    open(file_path, "w").close()
    open(doc_path, "w").close()

    return file_path


def create_new_type_file(project_path: Path, file_name: str | Path) -> Path:
    file_name = str(file_name) + ".hat"
    doc_file = file_name + ".md"
    file_path: Path = project_path / SOURCE_TYPES_PATH / file_name

    if file_path.is_file():
        raise FileExistsError(f"File {file_path}.hat already exists")

    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    doc_path = project_path / DOCS_TYPES_PATH / doc_file
    if doc_path.parent != Path("."):
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    open(file_path, "w").close()
    open(doc_path, "w").close()

    return file_path


def create_new_const_file(project_path: Path, file_name: str | Path) -> Path:
    file_name = str(file_name) + ".hat"
    doc_file = file_name + ".md"
    file_path: Path = project_path / SOURCE_FOLDER_NAME / file_name

    if file_path.is_file():
        raise FileExistsError(f"File {file_path}.hat already exists")

    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    doc_path = project_path / DOCS_FOLDER_NAME / doc_file
    if doc_path.parent != Path("."):
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    open(file_path, "w").close()
    open(doc_path, "w").close()

    return file_path
