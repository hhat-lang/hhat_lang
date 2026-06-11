"""
Project documentation update implementation.

For now, this module checks whether each H-hat code file under ``src/`` has a
matching Markdown documentation file under ``docs/``, delegates dialect-specific
signature synchronization to Heather helpers, renames stale documentation files
as orphans, and removes stale documented signatures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from hhat_lang.dialects.heather.grammar import doc_signatures as heather_doc_signatures
from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, IMPORTS_FOLDER_NAME, SOURCE_FOLDER_NAME
from hhat_lang.toolchain.project.utils import str_to_path


@dataclass(frozen=True)
class SignatureMismatch:
    """A code signature that is missing from, or differs from, the documentation."""

    code_file: Path
    doc_file: Path
    signature: heather_doc_signatures.CodeSignature
    reason: str


@dataclass(frozen=True)
class RemovedSignature:
    """A documented signature removed because the code signature no longer exists."""

    doc_file: Path
    name: str


@dataclass(frozen=True)
class OrphanedDoc:
    """A documentation file renamed because its code file no longer exists."""

    original_path: Path
    orphan_path: Path


@dataclass(frozen=True)
class DocumentationUpdateResult:
    """Summary of documentation files and signatures checked during an update."""

    created_docs: tuple[Path, ...]
    orphaned_docs: tuple[OrphanedDoc, ...]
    checked_signatures: tuple[heather_doc_signatures.CodeSignature, ...]
    removed_signatures: tuple[RemovedSignature, ...]
    updated_signatures: tuple[SignatureMismatch, ...]
    signature_mismatches: tuple[SignatureMismatch, ...]

    @property
    def created_count(self) -> int:
        return len(self.created_docs)

    @property
    def orphaned_doc_count(self) -> int:
        return len(self.orphaned_docs)

    @property
    def checked_signature_count(self) -> int:
        return len(self.checked_signatures)

    @property
    def removed_signature_count(self) -> int:
        return len(self.removed_signatures)

    @property
    def updated_signature_count(self) -> int:
        return len(self.updated_signatures)

    @property
    def signature_mismatch_count(self) -> int:
        return len(self.signature_mismatches)


def _is_in_hidden_dir(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _iter_code_files(source_root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (
                code_file
                for code_file in source_root.rglob("*.hat")
                if code_file.is_file()
                and IMPORTS_FOLDER_NAME not in code_file.parts
                and not _is_in_hidden_dir(code_file.relative_to(source_root))
            ),
            key=lambda path: path.as_posix(),
        )
    )


def _is_orphan_doc_file(doc_file: Path) -> bool:
    return re.match(r"^orphan\..+\.md$", doc_file.name) is not None


def _iter_doc_files(docs_root: Path) -> tuple[Path, ...]:
    if not docs_root.is_dir():
        return ()

    return tuple(
        sorted(
            (
                doc_file
                for doc_file in docs_root.rglob("*.md")
                if doc_file.is_file()
                and not _is_in_hidden_dir(doc_file.relative_to(docs_root))
                and not _is_orphan_doc_file(doc_file)
            ),
            key=lambda path: path.as_posix(),
        )
    )


def _code_counterpart(project_root: Path, doc_file: Path) -> Path:
    docs_root = project_root / DOCS_FOLDER_NAME
    relative_doc_file = doc_file.relative_to(docs_root)
    relative_code_file = relative_doc_file.with_suffix(".hat")
    return project_root / SOURCE_FOLDER_NAME / relative_code_file


def _doc_counterpart(project_root: Path, code_file: Path) -> Path:
    source_root = project_root / SOURCE_FOLDER_NAME
    relative_code_file = code_file.relative_to(source_root)
    relative_doc_file = relative_code_file.with_suffix(".md")
    return project_root / DOCS_FOLDER_NAME / relative_doc_file


def _update_documented_signatures(
    doc_file: Path,
    mismatches: tuple[SignatureMismatch, ...],
) -> None:
    markdown = doc_file.read_text(encoding="utf-8")
    for mismatch in mismatches:
        markdown = heather_doc_signatures.upsert_signature(markdown, mismatch.signature)
    doc_file.write_text(markdown, encoding="utf-8")


def _remove_stale_documented_signatures(
    doc_file: Path,
    signatures: tuple[heather_doc_signatures.CodeSignature, ...],
) -> tuple[RemovedSignature, ...]:
    markdown = doc_file.read_text(encoding="utf-8")
    sections = heather_doc_signatures.split_doc_sections(markdown)
    signature_names = {signature.name for signature in signatures}
    removed_signatures = tuple(
        RemovedSignature(doc_file=doc_file, name=name)
        for name, section in sections.items()
        if name not in signature_names
        and heather_doc_signatures.parse_documented_signature(section) is not None
    )

    for removed_signature in removed_signatures:
        markdown = heather_doc_signatures.remove_documented_signature(
            markdown, removed_signature.name
        )

    if removed_signatures:
        doc_file.write_text(markdown, encoding="utf-8")

    return removed_signatures


def _orphan_doc_path(doc_file: Path) -> Path:
    orphan_path = doc_file.with_name(f"orphan.{doc_file.name}")
    if not orphan_path.exists():
        return orphan_path

    counter = 1
    while True:
        candidate = doc_file.with_name(f"orphan.{doc_file.stem}.{counter}{doc_file.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _orphan_stale_doc_files(
    project_root: Path,
    docs_root: Path,
    code_files: tuple[Path, ...],
) -> tuple[OrphanedDoc, ...]:
    code_file_set = set(code_files)
    orphaned_docs: list[OrphanedDoc] = []
    for doc_file in _iter_doc_files(docs_root):
        code_file = _code_counterpart(project_root, doc_file)
        if code_file not in code_file_set:
            orphan_path = _orphan_doc_path(doc_file)
            doc_file.rename(orphan_path)
            orphaned_docs.append(OrphanedDoc(original_path=doc_file, orphan_path=orphan_path))

    return tuple(orphaned_docs)


def _check_signature_matches(
    code_file: Path,
    doc_file: Path,
    signatures: tuple[heather_doc_signatures.CodeSignature, ...],
) -> tuple[SignatureMismatch, ...]:
    if not doc_file.exists():
        return tuple(
            SignatureMismatch(
                code_file=code_file,
                doc_file=doc_file,
                signature=signature,
                reason="Documentation file is missing",
            )
            for signature in signatures
        )

    sections = heather_doc_signatures.split_doc_sections(doc_file.read_text(encoding="utf-8"))
    mismatches: list[SignatureMismatch] = []
    for signature in signatures:
        section = sections.get(signature.name)
        if section is None:
            mismatches.append(
                SignatureMismatch(
                    code_file=code_file,
                    doc_file=doc_file,
                    signature=signature,
                    reason="Signature section is missing",
                )
            )
            continue

        documented = heather_doc_signatures.parse_documented_signature(section)
        if documented is None:
            mismatches.append(
                SignatureMismatch(
                    code_file=code_file,
                    doc_file=doc_file,
                    signature=signature,
                    reason="Signature block is missing",
                )
            )
            continue

        mismatch_reason = heather_doc_signatures.signature_mismatch_reason(signature, documented)
        if mismatch_reason:
            mismatches.append(
                SignatureMismatch(
                    code_file=code_file,
                    doc_file=doc_file,
                    signature=signature,
                    reason=mismatch_reason,
                )
            )

    return tuple(mismatches)


def update_project(project_name: str | Path) -> DocumentationUpdateResult:
    """Create missing docs and check documented signatures against code signatures.

    The documentation tree mirrors the ``src/`` tree under ``docs/`` and uses
    ``.md`` as the documentation suffix. For example, ``src/foo/bar.hat`` maps
    to ``docs/foo/bar.md``.
    """

    project_root = str_to_path(project_name)
    source_root = project_root / SOURCE_FOLDER_NAME
    docs_root = project_root / DOCS_FOLDER_NAME

    if not source_root.is_dir():
        raise FileNotFoundError(f"Source folder not found: {source_root}")

    docs_root.mkdir(parents=True, exist_ok=True)

    code_files = _iter_code_files(source_root)
    orphaned_docs = _orphan_stale_doc_files(project_root, docs_root, code_files)

    created_docs: list[Path] = []
    checked_signatures: list[heather_doc_signatures.CodeSignature] = []
    removed_signatures: list[RemovedSignature] = []
    updated_signatures: list[SignatureMismatch] = []
    signature_mismatches: list[SignatureMismatch] = []

    for code_file in code_files:
        doc_file = _doc_counterpart(project_root, code_file)
        if not doc_file.exists():
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            doc_file.write_text(f"# {doc_file.stem}\n\n", encoding="utf-8")
            created_docs.append(doc_file)

        signatures = heather_doc_signatures.parse_code_signatures(code_file)
        checked_signatures.extend(signatures)
        removed_signatures.extend(_remove_stale_documented_signatures(doc_file, signatures))

        mismatches = _check_signature_matches(code_file, doc_file, signatures)
        if mismatches:
            _update_documented_signatures(doc_file, mismatches)
            updated_signatures.extend(mismatches)
            signature_mismatches.extend(_check_signature_matches(code_file, doc_file, signatures))

    return DocumentationUpdateResult(
        created_docs=tuple(created_docs),
        orphaned_docs=orphaned_docs,
        checked_signatures=tuple(checked_signatures),
        removed_signatures=tuple(removed_signatures),
        updated_signatures=tuple(updated_signatures),
        signature_mismatches=tuple(signature_mismatches),
    )
