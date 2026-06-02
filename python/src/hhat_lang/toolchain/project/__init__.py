from __future__ import annotations

from pathlib import Path

# base folder names
SOURCE_FOLDER_NAME = Path("src")
TYPES_FOLDER_NAME = Path("hat_types")
IMPORTS_FOLDER_NAME = Path(".hat_imports")  # must be a hidden folder
DOCS_FOLDER_NAME = Path("docs")
TESTS_FOLDER_NAME = Path("tests")  # future use
PROOFS_FOLDER_NAME = Path("proofs")  # future use

# files
MAIN_FILE_NAME = "main.hat"

MAIN_DOC_FILE_NAME = f"{Path(MAIN_FILE_NAME).stem}.md"

# paths
MAIN_PATH = SOURCE_FOLDER_NAME / MAIN_FILE_NAME
IMPORTS_PATH = SOURCE_FOLDER_NAME / IMPORTS_FOLDER_NAME
SOURCE_TYPES_PATH = SOURCE_FOLDER_NAME / TYPES_FOLDER_NAME
DOCS_TYPES_PATH = DOCS_FOLDER_NAME / TYPES_FOLDER_NAME
