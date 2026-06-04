"""
Update current files; It can be to create respective doc files for
the existing files.
"""

from __future__ import annotations

from pathlib import Path

from hhat_lang.dialects.heather.toolchain.docs import (
    extract_doc_signatures,
    render_doc_signatures,
)
from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, SOURCE_FOLDER_NAME
from hhat_lang.toolchain.project.docs import (
    ProjectDocBlockError,
    ProjectDocReadError,
    ProjectDocWriteError,
    ProjectSourceReadError,
    UpdateResult,
)
from hhat_lang.toolchain.project.utils import get_proj_dir, str_to_path

AUTO_START = "<!-- hhat-docs:auto:start -->"
AUTO_END = "<!-- hhat-docs:auto:end -->"


def update_project(project_name: str | Path) -> UpdateResult:
    project_root = get_proj_dir(str_to_path(project_name))
    source_root = project_root / SOURCE_FOLDER_NAME

    created_docs: list[Path] = []
    updated_docs: list[Path] = []
    unchanged_docs: list[Path] = []
    signature_count = 0

    for source_path in sorted(source_root.rglob("*.hat")):
        relative_source = source_path.relative_to(source_root)
        if any(part.startswith(".") for part in relative_source.parts):
            continue

        doc_path = _doc_path_for_source(project_root, source_path)
        try:
            source = source_path.read_text()
        except OSError as exc:
            raise ProjectSourceReadError(f"Could not read source file {source_path}") from exc

        signatures = extract_doc_signatures(source)
        signature_count += len(signatures)

        existed = doc_path.exists()
        changed = _write_doc_file(
            project_root,
            source_path,
            doc_path,
            render_doc_signatures(signatures),
        )

        if changed and existed:
            updated_docs.append(doc_path)
        elif changed:
            created_docs.append(doc_path)
        else:
            unchanged_docs.append(doc_path)

    return UpdateResult(
        created_docs=tuple(created_docs),
        updated_docs=tuple(updated_docs),
        unchanged_docs=tuple(unchanged_docs),
        orphan_docs=tuple(_find_orphan_docs(project_root)),
        signature_count=signature_count,
    )


def _doc_path_for_source(project_root: Path, source_path: Path) -> Path:
    relative_source = source_path.relative_to(project_root / SOURCE_FOLDER_NAME)
    return project_root / DOCS_FOLDER_NAME / relative_source.with_suffix(".md")


def _write_doc_file(
    project_root: Path,
    source_path: Path,
    doc_path: Path,
    rendered_signatures: str,
) -> bool:
    if doc_path.exists():
        try:
            old_content = doc_path.read_text()
        except OSError as exc:
            raise ProjectDocReadError(f"Could not read documentation file {doc_path}") from exc
    else:
        old_content = _new_doc_header(source_path)

    new_content = _sync_generated_block(old_content, rendered_signatures, doc_path)
    if new_content != old_content:
        try:
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(new_content)
        except OSError as exc:
            raise ProjectDocWriteError(f"Could not write documentation file {doc_path}") from exc
        return True

    return False


def _new_doc_header(source_path: Path) -> str:
    return f"# {source_path.stem}\n"


def _sync_generated_block(content: str, rendered_signatures: str, doc_path: Path) -> str:
    start = content.find(AUTO_START)
    end = content.find(AUTO_END)

    if (start == -1) != (end == -1):
        raise ProjectDocBlockError(
            f"Malformed generated documentation block in {doc_path}: "
            f"both {AUTO_START!r} and {AUTO_END!r} are required"
        )

    new_block = _generated_block(rendered_signatures)
    if start != -1:
        block_end = end + len(AUTO_END)
        return _clean_doc_spacing(content[:start] + new_block + content[block_end:])

    if not new_block:
        return content

    return _clean_doc_spacing(f"{content.rstrip()}\n\n{new_block}\n")


def _generated_block(rendered_signatures: str) -> str:
    rendered_signatures = rendered_signatures.strip()
    if not rendered_signatures:
        return ""
    return f"{AUTO_START}\n{rendered_signatures}\n{AUTO_END}"


def _clean_doc_spacing(content: str) -> str:
    return content.rstrip() + "\n"


def _find_orphan_docs(project_root: Path) -> list[Path]:
    docs_root = project_root / DOCS_FOLDER_NAME
    source_root = project_root / SOURCE_FOLDER_NAME
    if not docs_root.exists():
        return []

    orphan_docs: list[Path] = []
    for doc_path in sorted(docs_root.rglob("*.md")):
        relative_doc = doc_path.relative_to(docs_root)
        expected_source = source_root / relative_doc.with_suffix(".hat")
        if not expected_source.exists():
            orphan_docs.append(doc_path)
    return orphan_docs
