# mypy: ignore-errors
"""Public project-update API.

The implementation lives in :mod:`hhat_lang.toolchain.project.doc_update` so
``hhat_lang.toolchain.project.update`` stays as a small compatibility module for
callers that already import ``update_project`` from this path.
"""

from __future__ import annotations

from hhat_lang.toolchain.project.doc_update import (
    DocumentationUpdateResult,
    OrphanedDoc,
    RemovedSignature,
    SignatureMismatch,
    update_project,
)

__all__ = [
    "DocumentationUpdateResult",
    "OrphanedDoc",
    "RemovedSignature",
    "SignatureMismatch",
    "update_project",
]
