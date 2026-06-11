"""Heather signature parsing helpers."""

from __future__ import annotations

import re
from pathlib import Path

from hhat_lang.toolchain.project.doc_signatures import CodeSignature, SignatureRow

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
