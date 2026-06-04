from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocArgument:
    name: str
    type_name: str


@dataclass(frozen=True)
class DocSignature:
    name: str
    kind: str
    type_name: str | None = None
    arguments: tuple[DocArgument, ...] = ()
    members: tuple[DocArgument, ...] = ()


@dataclass(frozen=True)
class UpdateResult:
    created_docs: tuple[Path, ...]
    updated_docs: tuple[Path, ...]
    unchanged_docs: tuple[Path, ...]
    orphan_docs: tuple[Path, ...]
    signature_count: int


class ProjectUpdateError(Exception):
    """Base exception for project update failures."""


class ProjectSourceReadError(ProjectUpdateError):
    """Raised when a source file cannot be read."""


class ProjectDocReadError(ProjectUpdateError):
    """Raised when a documentation file cannot be read."""


class ProjectDocWriteError(ProjectUpdateError):
    """Raised when a documentation file cannot be written."""


class ProjectDocBlockError(ProjectUpdateError):
    """Raised when a generated documentation block is malformed."""
