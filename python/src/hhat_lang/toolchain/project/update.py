"""
Update current project files.

``hat update`` currently performs documentation/code matching checks:

* every H-hat source file under ``src/`` must have a markdown counterpart under
  ``docs/`` with the same relative path;
* function and type signatures declared in source files must match the
  signature sections documented in those markdown counterparts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from hhat_lang.dialects.heather.grammar.doc_signatures import (
    CodeSignature,
    ParameterSignature,
    VariantSignature,
    collect_code_signatures,
)
from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, SOURCE_FOLDER_NAME
from hhat_lang.toolchain.project.utils import str_to_path


@dataclass(frozen=True)
class SignatureMismatch:
    """A code/documentation signature mismatch for a source file."""

    code_file: Path
    doc_file: Path
    signature_name: str
    reason: str


@dataclass(frozen=True)
class SignatureUpdate:
    """A code signature that was written to documentation."""

    code_file: Path
    doc_file: Path
    signature_name: str
    reason: str


@dataclass(frozen=True)
class SignatureRemoval:
    """A documented signature that was removed because code no longer exists."""

    code_file: Path
    doc_file: Path
    signature_name: str
    reason: str


@dataclass(frozen=True)
class OrphanDocRename:
    """A documentation file renamed because the source file no longer exists."""

    doc_file: Path
    orphan_doc_file: Path
    reason: str


@dataclass(frozen=True)
class ProjectUpdateResult:
    """Result of synchronizing and checking project documentation."""

    created_doc_files: list[Path] = field(default_factory=list)
    renamed_doc_files: list[OrphanDocRename] = field(default_factory=list)
    updated_signatures: list[SignatureUpdate] = field(default_factory=list)
    removed_signatures: list[SignatureRemoval] = field(default_factory=list)
    signature_mismatches: list[SignatureMismatch] = field(default_factory=list)

    @property
    def has_signature_mismatches(self) -> bool:
        return bool(self.signature_mismatches)


def _parse_doc_table(
    section: str, header: str
) -> tuple[ParameterSignature | VariantSignature, ...]:
    table_match = re.search(
        rf"-\s+{re.escape(header)}:\s*\n(?P<table>.*?)(?=\n### |\n## |\Z)",
        section,
        flags=re.DOTALL,
    )
    if not table_match:
        return ()

    rows: list[ParameterSignature | VariantSignature] = []
    for line in table_match.group("table").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or header.split("/")[0] in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3 or cells[1] == "Type":
            continue
        if header == "Variants":
            rows.append(VariantSignature(cells[0], cells[1], cells[2]))
        else:
            rows.append(ParameterSignature(cells[0], cells[1], cells[2]))
    return tuple(rows)


def _render_signature_table(
    title: str, rows: tuple[ParameterSignature | VariantSignature, ...]
) -> list[str]:
    first_column = {
        "Arguments": "Argument",
        "Members/Fields": "Member/Field",
        "Variants": "Variant",
    }[title]
    lines = [
        f"- {title}:",
        "",
        f"  | {first_column} | Type | Paradigm |",
        "  | :--- | :--- | :--- |",
    ]
    lines.extend(f"  | {row.name} | {row.type} | {row.paradigm} |" for row in rows)
    return lines


def render_signature(signature: CodeSignature) -> str:
    """Render a code signature as the canonical markdown signature block."""
    lines = [
        "### Signature",
        f"- Name: {signature.name}",
    ]

    if signature.kind == "function":
        lines.append(f"- Type: {signature.type}")

    lines.extend(
        [
            f"- Kind: {signature.kind}",
            f"- Paradigm: {signature.paradigm}",
        ]
    )

    if signature.kind == "function":
        lines.extend(_render_signature_table("Arguments", signature.arguments))
    elif signature.kind == "struct":
        lines.extend(_render_signature_table("Members/Fields", signature.members))
    elif signature.kind == "enum":
        lines.extend(_render_signature_table("Variants", signature.variants))

    return "\n".join(lines).rstrip() + "\n"


def render_documented_signature_section(signature: CodeSignature) -> str:
    """Render a full markdown section for a newly documented signature."""
    return f"## {signature.name}\n\n{render_signature(signature)}\n### Documentation\n\n"


def _find_signature_section(content: str, signature_name: str) -> re.Match[str] | None:
    return re.search(rf"^##\s+{re.escape(signature_name)}\s*$", content, flags=re.MULTILINE)


def _next_heading(content: str, start: int, level: str) -> int:
    match = re.search(rf"^{level}\s+", content[start:], flags=re.MULTILINE)
    return start + match.start() if match else len(content)


def _replace_signature_in_section(
    content: str, section_match: re.Match[str], signature: CodeSignature
) -> tuple[str, bool]:
    section_body_start = section_match.end()
    section_end = _next_heading(content, section_body_start, "##")
    section = content[section_body_start:section_end]
    rendered_signature = render_signature(signature).rstrip()

    signature_match = re.search(r"^###\s+Signature\s*$", section, flags=re.MULTILINE)
    if signature_match:
        signature_start = section_body_start + signature_match.start()
        next_subsection = re.search(
            r"^###\s+", section[signature_match.end() :], flags=re.MULTILINE
        )
        signature_end = (
            section_body_start + signature_match.end() + next_subsection.start()
            if next_subsection
            else section_end
        )
        new_content = (
            content[:signature_start]
            + rendered_signature
            + "\n\n"
            + content[signature_end:].lstrip("\n")
        )
        return new_content, new_content != content

    documentation_match = re.search(r"^###\s+Documentation\s*$", section, flags=re.MULTILINE)
    insert_at = (
        section_body_start + documentation_match.start() if documentation_match else section_end
    )
    new_content = (
        content[:insert_at].rstrip()
        + "\n\n"
        + rendered_signature
        + "\n\n"
        + content[insert_at:].lstrip("\n")
    )
    return new_content, True


def upsert_doc_signatures_for_file(
    doc_file: str | Path, signatures: dict[str, CodeSignature]
) -> set[str]:
    """Insert or replace documented signature blocks for a markdown file."""
    doc_file = str_to_path(doc_file)
    content = doc_file.read_text(encoding="utf-8") if doc_file.exists() else f"# {doc_file.stem}\n"
    updated_signature_names: set[str] = set()

    for signature_name, signature in signatures.items():
        section_match = _find_signature_section(content, signature_name)
        if section_match is None:
            separator = "\n\n" if content.strip() else ""
            content = content.rstrip() + separator + render_documented_signature_section(signature)
            updated_signature_names.add(signature_name)
            continue

        content, changed = _replace_signature_in_section(content, section_match, signature)
        if changed:
            updated_signature_names.add(signature_name)

    if updated_signature_names:
        doc_file.write_text(content.rstrip() + "\n", encoding="utf-8")

    return updated_signature_names


def update_doc_signatures(project_root: str | Path) -> list[SignatureUpdate]:
    """Update missing or stale signature blocks in project markdown docs."""
    project_root = str_to_path(project_root)
    signature_updates: list[SignatureUpdate] = []

    for code_file in iter_code_files(project_root):
        doc_file = code_file_to_doc_file(project_root, code_file)
        code_signatures = collect_code_signatures(code_file)
        doc_signatures = collect_doc_signatures(doc_file)
        updated_signature_names = upsert_doc_signatures_for_file(doc_file, code_signatures)

        for signature_name in updated_signature_names:
            reason = (
                "missing from documentation"
                if signature_name not in doc_signatures
                else "documentation signature differed from code"
            )
            signature_updates.append(
                SignatureUpdate(
                    code_file=code_file,
                    doc_file=doc_file,
                    signature_name=signature_name,
                    reason=reason,
                )
            )

    return signature_updates


def collect_doc_signatures(doc_file: str | Path) -> dict[str, CodeSignature]:
    """Collect documented function and type signatures from a markdown file."""
    doc_file = str_to_path(doc_file)
    if not doc_file.exists():
        return {}

    content = doc_file.read_text(encoding="utf-8")
    signatures: dict[str, CodeSignature] = {}
    for match in re.finditer(r"^##\s+(?P<name>.+?)\s*$", content, flags=re.MULTILINE):
        name = match.group("name").strip()
        next_section = re.search(r"^##\s+", content[match.end() :], flags=re.MULTILINE)
        end = match.end() + next_section.start() if next_section else len(content)
        section = content[match.end() : end]
        if "### Signature" not in section:
            continue

        kind_match = re.search(r"^-\s+Kind:\s*(?P<value>.+?)\s*$", section, flags=re.MULTILINE)
        paradigm_match = re.search(
            r"^-\s+Paradigm:\s*(?P<value>.+?)\s*$", section, flags=re.MULTILINE
        )
        if not kind_match or not paradigm_match:
            continue

        documented_name_match = re.search(
            r"^-\s+Name:\s*(?P<value>.+?)\s*$", section, flags=re.MULTILINE
        )
        signature_name = (
            documented_name_match.group("value").strip() if documented_name_match else name
        )
        type_match = re.search(r"^-\s+Type:\s*(?P<value>.+?)\s*$", section, flags=re.MULTILINE)
        arguments = tuple(_parse_doc_table(section, "Arguments"))
        members = tuple(_parse_doc_table(section, "Members/Fields"))
        variants = tuple(_parse_doc_table(section, "Variants"))

        signatures[signature_name] = CodeSignature(
            name=signature_name,
            kind=kind_match.group("value").strip(),
            type=type_match.group("value").strip() if type_match else None,
            paradigm=paradigm_match.group("value").strip(),
            arguments=arguments,  # type: ignore[arg-type]
            members=members,  # type: ignore[arg-type]
            variants=variants,  # type: ignore[arg-type]
        )

    return signatures


def code_file_to_doc_file(project_root: str | Path, code_file: str | Path) -> Path:
    """Return the documentation path that corresponds to a source code file."""
    project_root = str_to_path(project_root)
    code_file = str_to_path(code_file)
    relative_code_file = code_file.relative_to(project_root / SOURCE_FOLDER_NAME)
    return project_root / DOCS_FOLDER_NAME / relative_code_file.with_suffix(".md")


def doc_file_to_code_file(project_root: str | Path, doc_file: str | Path) -> Path:
    """Return the source path that corresponds to a documentation file."""
    project_root = str_to_path(project_root)
    doc_file = str_to_path(doc_file)
    relative_doc_file = doc_file.relative_to(project_root / DOCS_FOLDER_NAME)
    return project_root / SOURCE_FOLDER_NAME / relative_doc_file.with_suffix(".hat")


def _is_project_owned_path(path: Path, root: Path) -> bool:
    return not any(part.startswith(".") for part in path.relative_to(root).parts)


def iter_code_files(project_root: str | Path) -> list[Path]:
    """Return all project-owned H-hat source files that require documentation."""
    project_root = str_to_path(project_root)
    source_root = project_root / SOURCE_FOLDER_NAME
    return sorted(
        code_file
        for code_file in source_root.rglob("*.hat")
        if _is_project_owned_path(code_file, source_root)
    )


def create_missing_doc_files(project_root: str | Path) -> list[Path]:
    """Create missing markdown counterparts for all H-hat source files."""
    project_root = str_to_path(project_root)
    created_doc_files: list[Path] = []

    for code_file in iter_code_files(project_root):
        doc_file = code_file_to_doc_file(project_root, code_file)
        if doc_file.exists():
            continue

        doc_file.parent.mkdir(parents=True, exist_ok=True)
        doc_file.write_text(f"# {doc_file.stem}\n\n", encoding="utf-8")
        created_doc_files.append(doc_file)

    return created_doc_files


def iter_doc_files(project_root: str | Path) -> list[Path]:
    """Return all project-owned markdown documentation files."""
    project_root = str_to_path(project_root)
    docs_root = project_root / DOCS_FOLDER_NAME
    if not docs_root.exists():
        return []

    return sorted(
        doc_file
        for doc_file in docs_root.rglob("*.md")
        if _is_project_owned_path(doc_file, docs_root)
    )


def _orphan_doc_file_path(doc_file: Path) -> Path:
    if doc_file.name.startswith("orphan."):
        return doc_file
    return doc_file.with_name(f"orphan.{doc_file.name}")


def rename_orphan_doc_files(project_root: str | Path) -> list[OrphanDocRename]:
    """Rename docs whose corresponding H-hat source file no longer exists."""
    project_root = str_to_path(project_root)
    renamed_doc_files: list[OrphanDocRename] = []

    for doc_file in iter_doc_files(project_root):
        if doc_file.name.startswith("orphan."):
            continue

        code_file = doc_file_to_code_file(project_root, doc_file)
        if code_file.exists():
            continue

        orphan_doc_file = _orphan_doc_file_path(doc_file)
        doc_file.replace(orphan_doc_file)
        renamed_doc_files.append(
            OrphanDocRename(
                doc_file=doc_file,
                orphan_doc_file=orphan_doc_file,
                reason="missing source code file",
            )
        )

    return renamed_doc_files


def _remove_signature_section(content: str, signature_name: str) -> tuple[str, bool]:
    section_match = _find_signature_section(content, signature_name)
    if section_match is None:
        return content, False

    section_end = _next_heading(content, section_match.end(), "##")
    new_content = (
        content[: section_match.start()].rstrip() + "\n\n" + content[section_end:].lstrip()
    )
    return new_content, new_content != content


def remove_stale_doc_signatures(project_root: str | Path) -> list[SignatureRemoval]:
    """Remove documented signature sections that no longer exist in source code."""
    project_root = str_to_path(project_root)
    signature_removals: list[SignatureRemoval] = []

    for code_file in iter_code_files(project_root):
        doc_file = code_file_to_doc_file(project_root, code_file)
        code_signatures = collect_code_signatures(code_file)
        doc_signatures = collect_doc_signatures(doc_file)
        stale_signature_names = sorted(set(doc_signatures) - set(code_signatures))
        if not stale_signature_names or not doc_file.exists():
            continue

        content = doc_file.read_text(encoding="utf-8")
        changed = False
        for signature_name in stale_signature_names:
            content, removed = _remove_signature_section(content, signature_name)
            if not removed:
                continue
            changed = True
            signature_removals.append(
                SignatureRemoval(
                    code_file=code_file,
                    doc_file=doc_file,
                    signature_name=signature_name,
                    reason="missing from source code",
                )
            )

        if changed:
            doc_file.write_text(content.rstrip() + "\n", encoding="utf-8")

    return signature_removals


def check_signature_matches(project_root: str | Path) -> list[SignatureMismatch]:
    """Check that code signatures are present and identical in their markdown docs."""
    project_root = str_to_path(project_root)
    mismatches: list[SignatureMismatch] = []

    for code_file in iter_code_files(project_root):
        doc_file = code_file_to_doc_file(project_root, code_file)
        code_signatures = collect_code_signatures(code_file)
        doc_signatures = collect_doc_signatures(doc_file)

        for signature_name, code_signature in code_signatures.items():
            doc_signature = doc_signatures.get(signature_name)
            if doc_signature is None:
                mismatches.append(
                    SignatureMismatch(
                        code_file=code_file,
                        doc_file=doc_file,
                        signature_name=signature_name,
                        reason="missing from documentation",
                    )
                )
                continue
            if doc_signature != code_signature:
                mismatches.append(
                    SignatureMismatch(
                        code_file=code_file,
                        doc_file=doc_file,
                        signature_name=signature_name,
                        reason="documentation signature differs from code",
                    )
                )

    return mismatches


def update_project(project_name: str | Path) -> ProjectUpdateResult:
    """Update a project by creating/renaming docs and synchronizing signatures."""
    project_name = str_to_path(project_name)
    created_doc_files = create_missing_doc_files(project_name)
    updated_signatures = update_doc_signatures(project_name)
    removed_signatures = remove_stale_doc_signatures(project_name)
    signature_mismatches = check_signature_matches(project_name)
    renamed_doc_files = rename_orphan_doc_files(project_name)
    return ProjectUpdateResult(
        created_doc_files,
        renamed_doc_files,
        updated_signatures,
        removed_signatures,
        signature_mismatches,
    )
