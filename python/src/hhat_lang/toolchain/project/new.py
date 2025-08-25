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
    TESTS_FOLDER_NAME,
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


def create_new_project(project_name: str | Path) -> Any:
    project_name = str_to_path(project_name)

    _create_template_folders(project_name)
    _create_template_files(project_name)


def _create_template_folders(project_name: Path) -> Any:
    # create root folder 'project_name' name
    os.mkdir(project_name)

    # create project template structure
    os.mkdir(project_name / SOURCE_FOLDER_NAME)
    os.mkdir(project_name / SOURCE_TYPES_PATH)
    os.mkdir(project_name / DOCS_FOLDER_NAME)
    os.mkdir(project_name / DOCS_TYPES_PATH)
    os.mkdir(project_name / TESTS_FOLDER_NAME)
    # os.mkdir(project_name / "proofs")  # TODO: once proofs are incorporated, include them


def _create_template_files(project_name: Path) -> Any:
    open(project_name / SOURCE_FOLDER_NAME / MAIN_FILE_NAME, "w").close()
    open(project_name / DOCS_FOLDER_NAME / MAIN_DOC_FILE_NAME, "w").close()


###################
# CREATE NEW FILE #
###################


def create_new_file(project_name: str | Path, file_name: str | Path) -> Path:
    project_name = str_to_path(project_name)
    file_name = str(file_name) + ".hat"
    doc_file = (
        file_name + ".md"
    )  # file_name.parent.parent / DOCS_FOLDER_NAME / (file_name.name + ".md")

    file_path: Path = project_name / SOURCE_FOLDER_NAME / file_name
    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    doc_path = project_name / DOCS_FOLDER_NAME / doc_file
    if doc_path.parent != Path("."):
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    open(file_path, "w").close()
    open(doc_path, "w").close()

    return file_path


def create_new_type_file(project_name: str | Path, file_name: str | Path) -> Path:
    project_name = str_to_path(project_name)
    file_name = str(file_name) + ".hat"
    doc_file = file_name + ".md"

    file_path: Path = project_name / SOURCE_TYPES_PATH / file_name
    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    doc_path = project_name / DOCS_TYPES_PATH / doc_file
    if doc_path.parent != Path("."):
        doc_path.parent.mkdir(parents=True, exist_ok=True)

    open(file_path, "w").close()
    open(doc_path, "w").close()

    return file_path
