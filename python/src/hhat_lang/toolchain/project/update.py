"""
Update current files; It can be to create respective doc files for
the existing files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, SOURCE_FOLDER_NAME
from hhat_lang.toolchain.project.utils import get_proj_dir, str_to_path

AUTO_START = "<!-- hhat-docs:auto:start -->"
AUTO_END = "<!-- hhat-docs:auto:end -->"

_IDENTIFIER = r"[#!%@]?[A-Za-z][A-Za-z0-9_-]*"
_TYPE_NAME = r"[#!%@]?[A-Za-z][A-Za-z0-9_\-\[\]]*"
_FN_RE = re.compile(
    rf"(?<![A-Za-z0-9_-])fn\s+(?P<name>{_IDENTIFIER})\s*"
    rf"\((?P<args>[^)]*)\)\s*(?P<return_type>{_TYPE_NAME})?\s*\{{",
    re.MULTILINE,
)
_ARG_RE = re.compile(rf"(?P<name>{_IDENTIFIER})\s*:\s*(?P<type>{_TYPE_NAME})")
_TYPE_RE = re.compile(rf"(?<![A-Za-z0-9_-])type\s+(?P<name>{_IDENTIFIER})")


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
        signatures = _extract_signatures(source_path.read_text())
        signature_count += len(signatures)

        existed = doc_path.exists()
        changed = _write_doc_file(project_root, source_path, doc_path, signatures)

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
    signatures: tuple[DocSignature, ...],
) -> bool:
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    old_content = doc_path.read_text() if doc_path.exists() else ""
    new_block = _render_generated_block(project_root, source_path, signatures)

    if AUTO_START in old_content and AUTO_END in old_content:
        start = old_content.index(AUTO_START)
        end = old_content.index(AUTO_END, start) + len(AUTO_END)
        new_content = old_content[:start] + new_block + old_content[end:]
    else:
        base_content = old_content.rstrip()
        if not base_content:
            base_content = f"# {source_path.stem}\n"
        new_content = f"{base_content}\n\n{new_block}\n"

    if new_content != old_content:
        doc_path.write_text(new_content)
        return True

    return False


def _render_generated_block(
    project_root: Path,
    source_path: Path,
    signatures: tuple[DocSignature, ...],
) -> str:
    relative_source = source_path.relative_to(project_root).as_posix()
    lines = [
        AUTO_START,
        f"_Generated from `{relative_source}`. Run `hat update` to refresh signatures._",
        "",
    ]

    if not signatures:
        lines.append("_No H-hat signatures found._")
    else:
        for signature in signatures:
            lines.extend(_render_signature(signature))
            lines.append("")

    lines.append(AUTO_END)
    return "\n".join(lines)


def _render_signature(signature: DocSignature) -> list[str]:
    lines = [
        f"## {signature.name}",
        "",
        "### Signature",
        "",
        f"- Name: `{signature.name}`",
        f"- Kind: {signature.kind}",
        f"- Paradigm: {_paradigm(signature.name, signature.type_name)}",
    ]

    if signature.type_name:
        lines.append(f"- Type: `{signature.type_name}`")

    if signature.arguments:
        lines.extend(["- Arguments:", "", "  | Argument | Type | Paradigm |"])
        lines.append("  | :--- | :--- | :--- |")
        for argument in signature.arguments:
            lines.append(
                f"  | `{argument.name}` | `{argument.type_name}` | "
                f"{_paradigm(argument.name, argument.type_name)} |"
            )

    if signature.members:
        lines.extend(["- Members:", "", "  | Member | Type | Paradigm |"])
        lines.append("  | :--- | :--- | :--- |")
        for member in signature.members:
            lines.append(
                f"  | `{member.name}` | `{member.type_name}` | "
                f"{_paradigm(member.name, member.type_name)} |"
            )

    return lines


def _extract_signatures(source: str) -> tuple[DocSignature, ...]:
    source = _strip_line_comments(source)
    signatures: list[DocSignature] = []
    signatures.extend(_extract_function_signatures(source))
    signatures.extend(_extract_type_signatures(source))
    return tuple(sorted(signatures, key=lambda signature: signature.name))


def _strip_line_comments(source: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in source.splitlines())


def _extract_function_signatures(source: str) -> list[DocSignature]:
    signatures: list[DocSignature] = []
    for match in _FN_RE.finditer(source):
        name = match.group("name")
        return_type = match.group("return_type") or "void"
        signatures.append(
            DocSignature(
                name=name,
                kind="function",
                type_name=return_type,
                arguments=_parse_arguments(match.group("args")),
            )
        )
    return signatures


def _extract_type_signatures(source: str) -> list[DocSignature]:
    signatures: list[DocSignature] = []
    index = 0
    while match := _TYPE_RE.search(source, index):
        name = match.group("name")
        cursor = _skip_spaces(source, match.end())
        type_name: str | None = None
        members: tuple[DocArgument, ...] = ()
        kind = "type"

        if cursor < len(source) and source[cursor] == ":":
            alias_start = _skip_spaces(source, cursor + 1)
            alias_match = re.match(_TYPE_NAME, source[alias_start:])
            if alias_match:
                type_name = alias_match.group(0)
                cursor = alias_start + alias_match.end()
            kind = "single type"
        elif cursor < len(source) and source[cursor] == "{":
            body, cursor = _read_braced_body(source, cursor)
            members = _parse_arguments(body)
            kind = "struct type" if members else "enum type"

        signatures.append(
            DocSignature(name=name, kind=kind, type_name=type_name, members=members)
        )
        index = cursor

    return signatures


def _parse_arguments(args_source: str) -> tuple[DocArgument, ...]:
    return tuple(
        DocArgument(match.group("name"), match.group("type"))
        for match in _ARG_RE.finditer(args_source)
    )


def _skip_spaces(source: str, index: int) -> int:
    while index < len(source) and source[index].isspace():
        index += 1
    return index


def _read_braced_body(source: str, open_index: int) -> tuple[str, int]:
    depth = 0
    for index in range(open_index, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[open_index + 1 : index], index + 1
    return source[open_index + 1 :], len(source)


def _paradigm(name: str, type_name: str | None) -> str:
    return (
        "quantum"
        if name.startswith("@") or (type_name or "").startswith("@")
        else "classical"
    )


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
