"""Heather documentation signature parsing and rendering helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_IDENTIFIER = r"@?[a-zA-Z][a-zA-Z0-9\-_]*"
_TYPE_VALUE = r"\[?@?[a-zA-Z][a-zA-Z0-9\-_.]*(?:<[^\s{}()]+>)?\]?"
_FUNCTION_RE = re.compile(
    rf"(?<![\w-])fn\s+(?P<name>{_IDENTIFIER})\s*"
    rf"\((?P<args>[^)]*)\)\s*(?P<type>{_TYPE_VALUE})?\s*\{{",
    re.MULTILINE,
)
_TYPE_RE = re.compile(rf"(?<![\w-])type\s+(?P<name>{_IDENTIFIER})", re.MULTILINE)
_ARG_RE = re.compile(rf"(?P<name>{_IDENTIFIER})\s*:\s*(?P<type>{_TYPE_VALUE})")
_FIELD_RE = _ARG_RE
_HEADING_RE = re.compile(r"^##\s+(?P<name>.+?)\s*$", re.MULTILINE)
_SIGNATURE_HEADING_RE = re.compile(r"^###\s+Signature\s*$", re.IGNORECASE | re.MULTILINE)
_BULLET_RE = re.compile(r"^-\s+(?P<key>[^:]+):\s*(?P<value>.*)$", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$", re.MULTILINE)


@dataclass(frozen=True)
class SignatureRow:
    """A named row within a signature table, such as an argument or member."""

    name: str
    type: str
    paradigm: str


@dataclass(frozen=True)
class CodeSignature:
    """A function or type signature collected from a Heather source file."""

    name: str
    kind: str
    paradigm: str
    type: str | None = None
    arguments: tuple[SignatureRow, ...] = ()
    members: tuple[SignatureRow, ...] = ()
    variants: tuple[SignatureRow, ...] = ()


@dataclass(frozen=True)
class DocumentedSignature:
    """A signature parsed from Markdown documentation."""

    name: str | None = None
    kind: str | None = None
    paradigm: str | None = None
    type: str | None = None
    arguments: tuple[SignatureRow, ...] = ()
    members: tuple[SignatureRow, ...] = ()
    variants: tuple[SignatureRow, ...] = ()


def strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return re.sub(r"//.*", "", code)


def paradigm(*values: str | None) -> str:
    if any(value and value.strip().startswith("@") for value in values):
        return "quantum"
    return "classical"


def _parse_rows(raw_rows: str) -> tuple[SignatureRow, ...]:
    return tuple(
        SignatureRow(
            name=match.group("name").strip(),
            type=match.group("type").strip(),
            paradigm=paradigm(match.group("name"), match.group("type")),
        )
        for match in _ARG_RE.finditer(raw_rows)
    )


def _parse_function_signatures(code: str) -> tuple[CodeSignature, ...]:
    signatures: list[CodeSignature] = []
    for match in _FUNCTION_RE.finditer(code):
        name = match.group("name").strip()
        function_type = (match.group("type") or "").strip()
        signatures.append(
            CodeSignature(
                name=name,
                kind="function",
                type=function_type,
                paradigm=paradigm(name),
                arguments=_parse_rows(match.group("args")),
            )
        )
    return tuple(signatures)


def _find_matching_brace(code: str, open_brace_index: int) -> int | None:
    depth = 0
    for index in range(open_brace_index, len(code)):
        if code[index] == "{":
            depth += 1
        elif code[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _parse_enum_variants(block: str) -> tuple[SignatureRow, ...]:
    variants: list[SignatureRow] = []
    index = 0
    while index < len(block):
        match = re.search(_IDENTIFIER, block[index:])
        if match is None:
            break

        name = match.group(0)
        name_start = index + match.start()
        index = index + match.end()
        next_index = index
        while next_index < len(block) and block[next_index].isspace():
            next_index += 1

        if next_index < len(block) and block[next_index] == ":":
            index = next_index + 1
            continue

        if next_index < len(block) and block[next_index] == "{":
            variants.append(SignatureRow(name=name, type="Tagged", paradigm=paradigm(name)))
            close_index = _find_matching_brace(block, next_index)
            index = len(block) if close_index is None else close_index + 1
            continue

        if name_start > 0 and block[name_start - 1] in {":", "."}:
            continue

        variants.append(SignatureRow(name=name, type="Named", paradigm=paradigm(name)))

    return tuple(variants)


def _parse_type_signatures(code: str) -> tuple[CodeSignature, ...]:
    signatures: list[CodeSignature] = []
    for match in _TYPE_RE.finditer(code):
        name = match.group("name").strip()
        index = match.end()
        while index < len(code) and code[index].isspace():
            index += 1

        if index < len(code) and code[index] == ":":
            line_end = code.find("\n", index)
            if line_end == -1:
                line_end = len(code)
            type_value = code[index + 1 : line_end].strip()
            signatures.append(
                CodeSignature(
                    name=name,
                    kind="primitive",
                    type=type_value,
                    paradigm=paradigm(name),
                )
            )
            continue

        if index >= len(code) or code[index] != "{":
            continue

        close_index = _find_matching_brace(code, index)
        if close_index is None:
            continue

        block = code[index + 1 : close_index]
        fields = tuple(
            SignatureRow(
                name=field.group("name").strip(),
                type=field.group("type").strip(),
                paradigm=paradigm(field.group("name"), field.group("type")),
            )
            for field in _FIELD_RE.finditer(block)
        )
        block_without_fields = _FIELD_RE.sub(" ", block).strip()
        has_tagged_variants = bool(re.search(rf"{_IDENTIFIER}\s*\{{", block))

        if fields and not block_without_fields and not has_tagged_variants:
            signatures.append(
                CodeSignature(
                    name=name,
                    kind="struct",
                    paradigm=paradigm(name),
                    members=fields,
                )
            )
        else:
            signatures.append(
                CodeSignature(
                    name=name,
                    kind="enum",
                    paradigm=paradigm(name),
                    variants=_parse_enum_variants(block),
                )
            )

    return tuple(signatures)


def parse_code_signatures(code_file: Path) -> tuple[CodeSignature, ...]:
    code = strip_comments(code_file.read_text(encoding="utf-8"))
    return _parse_function_signatures(code) + _parse_type_signatures(code)


def render_rows(label: str, columns: tuple[str, str, str], rows: tuple[SignatureRow, ...]) -> str:
    if not rows:
        return ""

    rendered = [
        f"- {label}:",
        "",
        f"  | {columns[0]} | {columns[1]} | {columns[2]} |",
        "  | :--- | :--- | :--- |",
    ]
    rendered.extend(f"  | {row.name} | {row.type} | {row.paradigm} |" for row in rows)
    return "\n".join(rendered) + "\n\n"


def render_signature_block(signature: CodeSignature) -> str:
    lines = [
        "### Signature",
        f"- Name: {signature.name}",
    ]
    if signature.type is not None:
        lines.append(f"- Type: {signature.type}")
    lines.extend(
        [
            f"- Kind: {signature.kind}",
            f"- Paradigm: {signature.paradigm}",
        ]
    )

    block = "\n".join(lines) + "\n"
    block += render_rows("Arguments", ("Argument", "Type", "Paradigm"), signature.arguments)
    block += render_rows("Members/Fields", ("Member/Field", "Type", "Paradigm"), signature.members)
    block += render_rows("Variants", ("Variant", "Type", "Paradigm"), signature.variants)
    return block.rstrip() + "\n\n"


def render_signature_section(signature: CodeSignature) -> str:
    return f"## {signature.name}\n\n{render_signature_block(signature)}### Documentation\n\n"


def find_signature_section(markdown: str, signature_name: str) -> re.Match[str] | None:
    heading_re = re.compile(rf"^##\s+{re.escape(signature_name)}\s*$", re.MULTILINE)
    return heading_re.search(markdown)


def find_next_section_start(markdown: str, start: int) -> int:
    match = _HEADING_RE.search(markdown, start)
    return match.start() if match else len(markdown)


def line_end(markdown: str, start: int) -> int:
    newline = markdown.find("\n", start)
    return len(markdown) if newline == -1 else newline + 1


def find_signature_block_end(markdown: str, signature_start: int, section_end: int) -> int:
    position = line_end(markdown, signature_start)
    while position < section_end:
        line_end_index = line_end(markdown, position)
        line = markdown[position:line_end_index]
        stripped = line.strip()
        if stripped.startswith("### "):
            return position
        if not stripped or stripped.startswith("-") or stripped.startswith("|"):
            position = line_end_index
            continue
        return position
    return section_end


def replace_range(markdown: str, start: int, end: int, replacement: str) -> str:
    prefix = markdown[:start].rstrip()
    suffix = markdown[end:].lstrip("\n")
    if suffix:
        return f"{prefix}\n\n{replacement}{suffix}"
    return f"{prefix}\n\n{replacement}".rstrip() + "\n"


def upsert_signature(markdown: str, signature: CodeSignature) -> str:
    section_match = find_signature_section(markdown, signature.name)
    signature_block = render_signature_block(signature)

    if section_match is None:
        separator = "" if markdown.endswith("\n\n") else "\n" if markdown.endswith("\n") else "\n\n"
        return markdown + separator + render_signature_section(signature)

    section_end = find_next_section_start(markdown, section_match.end())
    section_text = markdown[section_match.end() : section_end]
    has_documentation_heading = "### Documentation" in section_text
    replacement = signature_block
    if not has_documentation_heading:
        replacement += "### Documentation\n\n"

    signature_match = _SIGNATURE_HEADING_RE.search(markdown, section_match.end(), section_end)
    if signature_match is None:
        insertion_point = line_end(markdown, section_match.start())
        return (
            markdown[:insertion_point]
            + "\n"
            + replacement
            + markdown[insertion_point:].lstrip("\n")
        )

    signature_end = find_signature_block_end(markdown, signature_match.start(), section_end)
    return replace_range(markdown, signature_match.start(), signature_end, replacement)


def remove_documented_signature(markdown: str, signature_name: str) -> str:
    section_match = find_signature_section(markdown, signature_name)
    if section_match is None:
        return markdown

    section_end = find_next_section_start(markdown, section_match.end())
    signature_match = _SIGNATURE_HEADING_RE.search(markdown, section_match.end(), section_end)
    if signature_match is None:
        return markdown

    signature_end = find_signature_block_end(markdown, signature_match.start(), section_end)
    return replace_range(markdown, signature_match.start(), signature_end, "")


def split_doc_sections(markdown: str) -> dict[str, str]:
    matches = list(_HEADING_RE.finditer(markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group("name").strip()] = markdown[start:end]
    return sections


def parse_table_rows(section: str, table_label: str) -> tuple[SignatureRow, ...]:
    label_match = re.search(rf"^-\s+{re.escape(table_label)}:\s*$", section, re.MULTILINE)
    if not label_match:
        return ()

    rows: list[SignatureRow] = []
    table_text = section[label_match.end() :]
    for row_match in _TABLE_ROW_RE.finditer(table_text):
        cells = [cell.strip() for cell in row_match.group("cells").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() in {"argument", "member/field", "variant"}:
            continue
        if set(cells[0]) <= {":", "-"}:
            continue
        rows.append(SignatureRow(name=cells[0], type=cells[1], paradigm=cells[2]))
    return tuple(rows)


def parse_documented_signature(section: str) -> DocumentedSignature | None:
    signature_match = _SIGNATURE_HEADING_RE.search(section)
    if not signature_match:
        return None

    signature_section = section[signature_match.end() :]
    bullets = {
        match.group("key").strip().lower(): match.group("value").strip()
        for match in _BULLET_RE.finditer(signature_section)
    }
    return DocumentedSignature(
        name=bullets.get("name"),
        kind=bullets.get("kind"),
        paradigm=bullets.get("paradigm"),
        type=bullets.get("type"),
        arguments=parse_table_rows(signature_section, "Arguments"),
        members=parse_table_rows(signature_section, "Members/Fields"),
        variants=parse_table_rows(signature_section, "Variants"),
    )


def signature_mismatch_reason(
    expected: CodeSignature,
    documented: DocumentedSignature,
) -> str | None:
    expected_values: dict[str, object] = {
        "Name": expected.name,
        "Kind": expected.kind,
        "Paradigm": expected.paradigm,
    }
    if expected.type is not None:
        expected_values["Type"] = expected.type
    if expected.arguments:
        expected_values["Arguments"] = expected.arguments
    if expected.members:
        expected_values["Members/Fields"] = expected.members
    if expected.variants:
        expected_values["Variants"] = expected.variants

    documented_values: dict[str, object | None] = {
        "Name": documented.name,
        "Kind": documented.kind,
        "Paradigm": documented.paradigm,
        "Type": documented.type,
        "Arguments": documented.arguments,
        "Members/Fields": documented.members,
        "Variants": documented.variants,
    }

    mismatched_fields = [
        field
        for field, expected_value in expected_values.items()
        if documented_values.get(field) != expected_value
    ]
    if mismatched_fields:
        return "Mismatched signature field(s): " + ", ".join(mismatched_fields)
    return None
