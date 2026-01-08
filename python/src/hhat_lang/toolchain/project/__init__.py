from __future__ import annotations

# base folder names
SOURCE_FOLDER_NAME = "src"
TYPES_FOLDER_NAME = "hat_types"
IMPORTS_FOLDER_NAME = ".hat_imports"  # must be a hidden folder
DOCS_FOLDER_NAME = "docs"
TESTS_FOLDER_NAME = "tests"  # future use
PROOFS_FOLDER_NAME = "proofs"  # future use

# files
MAIN_FILE_NAME = "main.hat"

MAIN_DOC_FILE_NAME = f"{MAIN_FILE_NAME}.md"

# paths
MAIN_PATH = SOURCE_FOLDER_NAME / MAIN_DOC_FILE_NAME
IMPORTS_PATH = f"{SOURCE_FOLDER_NAME}/{IMPORTS_FOLDER_NAME}"
SOURCE_TYPES_PATH = f"{SOURCE_FOLDER_NAME}/{TYPES_FOLDER_NAME}"
DOCS_TYPES_PATH = f"{DOCS_FOLDER_NAME}/{TYPES_FOLDER_NAME}"
