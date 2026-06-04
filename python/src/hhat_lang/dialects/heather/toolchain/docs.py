from __future__ import annotations

import re

from hhat_lang.toolchain.project.docs import DocArgument, DocSignature

_IDENTIFIER = r"[#!%@]?[A-Za-z][A-Za-z0-9_-]*"
_TYPE_NAME = r"[#!%@]?[A-Za-z][A-Za-z0-9_\-\[\]]*"
_FN_RE = re.compile(
    rf"(?<![A-Za-z0-9_-])fn\s+(?P<name>{_IDENTIFIER})\s*"
    rf"\((?P<args>[^)]*)\)\s*(?P<return_type>{_TYPE_NAME})?\s*\{{",
    re.MULTILINE,
)
_ARG_RE = re.compile(rf"(?P<name>{_IDENTIFIER})\s*:\s*(?P<type>{_TYPE_NAME})")
_TYPE_RE = re.compile(rf"(?<![A-Za-z0-9_-])type\s+(?P<name>{_IDENTIFIER})")


def extract_doc_signatures(source: str) -> tuple[DocSignature, ...]:
    source = _strip_line_comments(source)
    signatures: list[DocSignature] = []
    signatures.extend(_extract_function_signatures(source))
    signatures.extend(_extract_type_signatures(source))
    return tuple(sorted(signatures, key=lambda signature: signature.name))


def render_doc_signatures(signatures: tuple[DocSignature, ...]) -> str:
    lines: list[str] = []
    for signature in signatures:
        lines.extend(_render_signature(signature))
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_signature(signature: DocSignature) -> list[str]:
    lines = [
        f"## {signature.name}",
        "",
        "### Signature",
        "",
        f"- Name: `{signature.name}`",
        f"- Name paradigm: {_paradigm(signature.name)}",
        f"- Kind: {signature.kind}",
    ]

    if signature.type_name:
        lines.extend(
            [
                f"- Type: `{signature.type_name}`",
                f"- Type paradigm: {_paradigm(signature.type_name)}",
            ]
        )

    if signature.arguments:
        lines.extend(
            [
                "- Arguments:",
                "",
                "  | Argument | Argument paradigm | Type | Type paradigm |",
            ]
        )
        lines.append("  | :--- | :--- | :--- | :--- |")
        for argument in signature.arguments:
            lines.append(
                f"  | `{argument.name}` | {_paradigm(argument.name)} | "
                f"`{argument.type_name}` | {_paradigm(argument.type_name)} |"
            )

    if signature.members:
        lines.extend(["- Members:", "", "  | Member | Member paradigm | Type | Type paradigm |"])
        lines.append("  | :--- | :--- | :--- | :--- |")
        for member in signature.members:
            lines.append(
                f"  | `{member.name}` | {_paradigm(member.name)} | "
                f"`{member.type_name}` | {_paradigm(member.type_name)} |"
            )

    return lines


def _strip_line_comments(source: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in source.splitlines())


def _extract_function_signatures(source: str) -> list[DocSignature]:
    signatures: list[DocSignature] = []
    for match in _FN_RE.finditer(source):
        return_type = match.group("return_type") or "void"
        signatures.append(
            DocSignature(
                name=match.group("name"),
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

        signatures.append(DocSignature(name=name, kind=kind, type_name=type_name, members=members))
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


def _paradigm(name: str) -> str:
    return "quantum" if name.startswith("@") else "classical"
