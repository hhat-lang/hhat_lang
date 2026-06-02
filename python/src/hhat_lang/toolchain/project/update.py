"""
Update current files; It can be to create respective doc files for
the existing files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, SOURCE_FOLDER_NAME
from hhat_lang.toolchain.project.utils import str_to_path


@dataclass(frozen=True)
class SignatureField:
    """A named type-bearing entry in a generated documentation signature."""

    name: str
    type: str


@dataclass(frozen=True)
class Signature:
    """Structured top-level H-hat declaration used to render documentation."""

    name: str
    kind: str
    paradigm: str
    type: str = ""
    arguments: tuple[SignatureField, ...] = ()
    members: tuple[SignatureField, ...] = ()
    variants: tuple[SignatureField, ...] = ()


@dataclass(frozen=True)
class UpdateSummary:
    """Summary of documentation changes made by ``hat update``."""

    created_docs: int
    updated_docs: int
    orphaned_docs: int


def update_project(project_name: str | Path) -> UpdateSummary:
    """Synchronize a project's ``docs/`` tree with top-level ``.hat`` files.

    The update step mirrors every ``src/**/*.hat`` file to ``docs/**/*.md``,
    renders function and type signatures, preserves existing free-form
    documentation sections, and renames documentation files without a source
    counterpart to ``orphan.<name>.md``.
    """

    project_root = str_to_path(project_name)
    src_root = project_root / SOURCE_FOLDER_NAME
    docs_root = project_root / DOCS_FOLDER_NAME

    if not src_root.is_dir():
        raise ValueError(f"Source folder not found: {src_root}")

    docs_root.mkdir(parents=True, exist_ok=True)

    expected_docs: set[Path] = set()
    created_docs = 0
    updated_docs = 0

    for code_path in _iter_code_files(src_root):
        relative_code_path = code_path.relative_to(src_root)
        doc_path = docs_root / relative_code_path.with_suffix(".md")
        legacy_doc_path = docs_root / Path(str(relative_code_path) + ".md")
        existing_doc_path = _first_existing_path(doc_path, legacy_doc_path)
        existing_content = existing_doc_path.read_text() if existing_doc_path else ""

        signatures = parse_code_signatures(code_path.read_text())
        new_content = render_doc_content(relative_code_path, signatures, existing_content)

        doc_path.parent.mkdir(parents=True, exist_ok=True)
        expected_docs.add(doc_path.resolve())

        if not doc_path.exists():
            created_docs += 1
            doc_path.write_text(new_content)
        elif doc_path.read_text() != new_content:
            updated_docs += 1
            doc_path.write_text(new_content)

    orphaned_docs = _rename_orphan_docs(docs_root, expected_docs)

    return UpdateSummary(
        created_docs=created_docs,
        updated_docs=updated_docs,
        orphaned_docs=orphaned_docs,
    )


def parse_code_signatures(code: str) -> tuple[Signature, ...]:
    """Extract supported top-level function and type signatures from H-hat code."""

    clean_code = _strip_comments(code)
    signatures = [*_parse_function_signatures(clean_code), *_parse_type_signatures(clean_code)]
    return tuple(sorted(signatures, key=lambda item: (item.name, item.kind, item.type)))


def render_doc_content(
    relative_code_path: Path,
    signatures: tuple[Signature, ...],
    existing_content: str = "",
) -> str:
    """Render a mirrored Markdown documentation file for a source file."""

    existing_docs = _extract_existing_documentation(existing_content)
    header = _extract_existing_header(existing_content)
    if not header.strip():
        header = f"# {relative_code_path.with_suffix('').as_posix()}\n"

    sections = [header.rstrip(), ""]
    for signature in signatures:
        documentation = existing_docs.get(signature.name, "").strip()
        sections.append(_render_signature_section(signature, documentation))

    return "\n\n".join(section for section in sections if section != "").rstrip() + "\n"


def _iter_code_files(src_root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in src_root.rglob("*.hat")
            if ".hat_imports" not in path.relative_to(src_root).parts
        )
    )


def _first_existing_path(*paths: Path) -> Path | None:
    return next((path for path in paths if path.exists()), None)


def _strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return re.sub(r"//.*", "", code)


def _parse_function_signatures(code: str) -> tuple[Signature, ...]:
    function_pattern = re.compile(
        r"(?<![\w-])fn\s+"
        r"(?P<name>@?[A-Za-z_][A-Za-z0-9_-]*)\s*"
        r"\((?P<args>[^)]*)\)\s*"
        r"(?P<type>[^\s{]+)?\s*\{",
        re.MULTILINE,
    )

    signatures = []
    for match in function_pattern.finditer(code):
        name = match.group("name")
        return_type = (match.group("type") or "null").strip()
        signatures.append(
            Signature(
                name=name,
                type=return_type,
                kind="function",
                paradigm=_paradigm(name, return_type),
                arguments=_parse_typed_fields(match.group("args")),
            )
        )

    return tuple(signatures)


def _parse_type_signatures(code: str) -> tuple[Signature, ...]:
    signatures: list[Signature] = []
    pattern = re.compile(r"(?<![\w-])type\s+(?P<name>@?[A-Za-z_][A-Za-z0-9_-]*)")
    index = 0

    while True:
        match = pattern.search(code, index)
        if match is None:
            break

        name = match.group("name")
        cursor = _skip_spaces(code, match.end())
        if cursor < len(code) and code[cursor] == ":":
            type_name, index = _read_type_alias(code, cursor + 1)
            signatures.append(
                Signature(
                    name=name,
                    type=type_name,
                    kind="primitive",
                    paradigm=_paradigm(name, type_name),
                )
            )
        elif cursor < len(code) and code[cursor] == "{":
            body, index = _read_braced_block(code, cursor)
            signatures.append(_signature_from_type_body(name, body))
        else:
            index = match.end()

    return tuple(signatures)


def _skip_spaces(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _read_type_alias(code: str, index: int) -> tuple[str, int]:
    index = _skip_spaces(code, index)
    start = index
    while index < len(code) and not code[index].isspace() and code[index] not in "{}":
        index += 1
    return code[start:index].strip(), index


def _read_braced_block(code: str, index: int) -> tuple[str, int]:
    depth = 0
    start = index + 1

    for cursor in range(index, len(code)):
        if code[cursor] == "{":
            depth += 1
        elif code[cursor] == "}":
            depth -= 1
            if depth == 0:
                return code[start:cursor], cursor + 1

    raise ValueError("Unclosed type body")


def _signature_from_type_body(name: str, body: str) -> Signature:
    items = _parse_body_items(body)
    if items and all(":" in item and "{" not in item for item in items):
        members = tuple(
            SignatureField(field_name, field_type)
            for field_name, field_type in (_split_typed_item(item) for item in items)
        )
        return Signature(
            name=name,
            kind="struct",
            paradigm=_paradigm(name, *(field.type for field in members)),
            members=members,
        )

    variants = tuple(SignatureField(_variant_name(item), _variant_type(item)) for item in items)
    return Signature(
        name=name,
        kind="enum",
        paradigm=_paradigm(name),
        variants=variants,
    )


def _parse_body_items(body: str) -> tuple[str, ...]:
    items: list[str] = []
    cursor = 0

    while cursor < len(body):
        cursor = _skip_spaces(body, cursor)
        if cursor >= len(body):
            break

        start = cursor
        while cursor < len(body) and not body[cursor].isspace() and body[cursor] != "{":
            cursor += 1

        head = body[start:cursor].strip()
        cursor = _skip_spaces(body, cursor)
        if cursor < len(body) and body[cursor] == "{":
            braced_body, cursor = _read_braced_block(body, cursor)
            items.append(f"{head} {{{braced_body.strip()}}}")
        elif head:
            items.append(head)

    return tuple(items)


def _parse_typed_fields(text: str) -> tuple[SignatureField, ...]:
    fields = []
    field_pattern = re.compile(r"(@?[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*([@\[\]A-Za-z0-9_-]+)")
    for name, field_type in field_pattern.findall(text):
        fields.append(SignatureField(name=name, type=field_type))
    return tuple(fields)


def _split_typed_item(item: str) -> tuple[str, str]:
    name, field_type = item.split(":", maxsplit=1)
    return name.strip(), field_type.strip()


def _variant_name(item: str) -> str:
    return item.split("{", maxsplit=1)[0].strip()


def _variant_type(item: str) -> str:
    return "Tagged" if "{" in item else "Named"


def _paradigm(*values: str) -> str:
    return (
        "quantum"
        if any(value.strip().startswith("@") for value in values if value)
        else "classical"
    )


def _extract_existing_header(content: str) -> str:
    match = re.search(r"^##\s+", content, flags=re.MULTILINE)
    if match is None:
        return content.strip()
    return content[: match.start()].strip()


def _extract_existing_documentation(content: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    section_pattern = re.compile(r"^##\s+(?P<name>.+?)\s*$", re.MULTILINE)
    matches = list(section_pattern.finditer(content))

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        section = content[start:end]
        doc_match = re.search(r"^###\s+Documentation\s*$", section, flags=re.MULTILINE)
        if doc_match:
            docs[match.group("name").strip()] = section[doc_match.end() :].strip()

    return docs


def _render_signature_section(signature: Signature, documentation: str) -> str:
    parts = [
        f"## {signature.name}",
        "",
        "### Signature",
        "",
        f"- Name: {signature.name}",
        *_render_signature_details(signature),
        "",
        "### Documentation",
        "",
        documentation,
    ]
    return "\n".join(parts).rstrip()


def _render_signature_details(signature: Signature) -> list[str]:
    details = [
        f"- Kind: {signature.kind}",
        f"- Paradigm: {signature.paradigm}",
    ]

    if signature.kind == "function":
        details.insert(0, f"- Type: {signature.type}")
        details.extend(_render_field_table("Arguments", "Argument", signature.arguments))
    elif signature.kind == "struct":
        details.extend(_render_field_table("Members/Fields", "Member/Field", signature.members))
    elif signature.kind == "enum":
        details.extend(_render_field_table("Variants", "Variant", signature.variants))
    elif signature.type:
        details.insert(0, f"- Type: {signature.type}")

    return details


def _render_field_table(
    title: str,
    first_column: str,
    fields: tuple[SignatureField, ...],
) -> list[str]:
    if not fields:
        return [f"- {title}: None"]

    lines = [
        f"- {title}:",
        "",
        f"  | {first_column} | Type | Paradigm |",
        "  | :--- | :--- | :--- |",
    ]
    lines.extend(
        f"  | {field.name} | {field.type} | {_paradigm(field.name, field.type)} |"
        for field in fields
    )
    return lines


def _rename_orphan_docs(docs_root: Path, expected_docs: set[Path]) -> int:
    orphaned_docs = 0

    for doc_path in sorted(docs_root.rglob("*.md")):
        if doc_path.resolve() in expected_docs or doc_path.name.startswith("orphan."):
            continue

        orphan_path = _next_orphan_path(doc_path)
        doc_path.rename(orphan_path)
        orphaned_docs += 1

    return orphaned_docs


def _next_orphan_path(doc_path: Path) -> Path:
    candidate = doc_path.with_name(f"orphan.{doc_path.name}")
    counter = 1
    while candidate.exists():
        candidate = doc_path.with_name(f"orphan.{counter}.{doc_path.name}")
        counter += 1
    return candidate
