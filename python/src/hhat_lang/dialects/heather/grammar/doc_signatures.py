"""Heather signature extraction used by documentation tooling.

This module owns the Heather syntax details needed to summarize code for
``hat update``.  Keeping this here lets the project-level CLI stay focused on
file synchronization and markdown handling instead of embedding dialect grammar
rules directly in the toolchain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParameterSignature:
    """Signature data for a function argument or type member."""

    name: str
    type: str
    paradigm: str


@dataclass(frozen=True)
class VariantSignature:
    """Signature data for an enum variant."""

    name: str
    type: str
    paradigm: str


@dataclass(frozen=True)
class CodeSignature:
    """A function or type signature found in Heather code or documentation."""

    name: str
    kind: str
    paradigm: str
    type: str | None = None
    arguments: tuple[ParameterSignature, ...] = ()
    members: tuple[ParameterSignature, ...] = ()
    variants: tuple[VariantSignature, ...] = ()


def _paradigm(*values: str | None) -> str:
    return (
        "quantum"
        if any(value and value.strip().startswith("@") for value in values)
        else "classical"
    )


def _strip_comments(content: str) -> str:
    return re.sub(r"//.*", "", content)


def _split_signature_items(content: str) -> list[str]:
    return [item.strip() for item in re.split(r"[\s,]+", content.strip()) if item.strip()]


def _parse_parameters(content: str) -> tuple[ParameterSignature, ...]:
    parameters: list[ParameterSignature] = []
    for item in _split_signature_items(content):
        if ":" not in item:
            continue
        name, type_name = [part.strip() for part in item.split(":", 1)]
        parameters.append(ParameterSignature(name, type_name, _paradigm(name, type_name)))
    return tuple(parameters)


def _parse_variants(content: str) -> tuple[VariantSignature, ...]:
    variants: list[VariantSignature] = []
    remaining = content.strip()
    while remaining:
        remaining = remaining.lstrip()
        match = re.match(r"(?P<name>@?[\w-]+)\s*(?:\{(?P<body>[^{}]*)\})?", remaining)
        if not match:
            break
        name = match.group("name")
        variant_type = "Tagged" if match.group("body") is not None else "Named"
        variants.append(VariantSignature(name, variant_type, _paradigm(name)))
        remaining = remaining[match.end() :]
    return tuple(variants)


def collect_code_signatures(code_file: str | Path) -> dict[str, CodeSignature]:
    """Collect function and type signatures from a Heather source file."""
    code_file = Path(code_file)
    content = _strip_comments(code_file.read_text(encoding="utf-8"))
    signatures: dict[str, CodeSignature] = {}

    for match in re.finditer(
        r"\bfn\s+(?P<name>@?[\w-]+)\s*\((?P<args>[^)]*)\)\s*(?P<type>@?[\w-]+)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    ):
        name = match.group("name")
        type_name = match.group("type")
        signatures[name] = CodeSignature(
            name=name,
            kind="function",
            type=type_name,
            paradigm=_paradigm(name, type_name),
            arguments=_parse_parameters(match.group("args")),
        )

    for match in re.finditer(
        r"\btype\s+(?P<name>@?[\w-]+)\s*\{(?P<body>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
        content,
        flags=re.MULTILINE | re.DOTALL,
    ):
        name = match.group("name")
        body = match.group("body")
        body_items = _split_signature_items(re.sub(r"\{[^{}]*\}", "", body))
        kind = "enum" if "{" in body or any(":" not in item for item in body_items) else "struct"
        signatures[name] = CodeSignature(
            name=name,
            kind=kind,
            paradigm=_paradigm(name),
            members=_parse_parameters(body) if kind == "struct" else (),
            variants=_parse_variants(body) if kind == "enum" else (),
        )

    return signatures
