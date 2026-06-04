"""
Update current files; It can be to create respective doc files for
the existing files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from hhat_lang.toolchain.project import DOCS_FOLDER_NAME, SOURCE_FOLDER_NAME, TYPES_FOLDER_NAME
from hhat_lang.toolchain.project.utils import get_proj_dir, str_to_path

AUTO_START = "<!-- hhat:auto-signatures:start -->"
AUTO_END = "<!-- hhat:auto-signatures:end -->"


@dataclass(frozen=True)
class ArgumentSignature:
    name: str
    type: str

    @property
    def paradigm(self) -> str:
        return _paradigm_for(self.name, self.type)


@dataclass(frozen=True)
class Signature:
    name: str
    kind: str
    type: str | None = None
    arguments: tuple[ArgumentSignature, ...] = ()
    members: tuple[ArgumentSignature, ...] = ()
    variants: tuple[str, ...] = ()

    @property
    def paradigm(self) -> str:
        parts = [self.name]
        if self.type:
            parts.append(self.type)
        parts.extend(arg.name for arg in self.arguments)
        parts.extend(arg.type for arg in self.arguments)
        parts.extend(member.name for member in self.members)
        parts.extend(member.type for member in self.members)
        return "quantum" if any(part.startswith("@") for part in parts) else "classical"


def update_project(project_name: str | Path) -> Any:
    project_path = _resolve_project_path(project_name)
    source_path = project_path / SOURCE_FOLDER_NAME
    docs_path = project_path / DOCS_FOLDER_NAME
    docs_path.mkdir(exist_ok=True)

    updated_files = 0
    updated_signatures = 0

    for source_file in _iter_source_files(source_path):
        signatures = tuple(_parse_signatures(source_file))
        doc_file = _doc_path_for(project_path, source_file)
        _write_doc_signatures(doc_file, signatures)
        updated_files += 1
        updated_signatures += len(signatures)

    return {"files": updated_files, "signatures": updated_signatures}


def _resolve_project_path(project_name: str | Path) -> Path:
    project_path = str_to_path(project_name)
    if not (project_path / SOURCE_FOLDER_NAME / "main.hat").exists():
        project_path = get_proj_dir(project_path)
    return project_path


def _iter_source_files(source_path: Path) -> Iterable[Path]:
    for source_file in sorted(source_path.rglob("*.hat")):
        if ".hat_imports" in source_file.parts:
            continue
        yield source_file


def _parse_signatures(source_file: Path) -> Iterable[Signature]:
    content = _strip_line_comments(source_file.read_text())
    if _is_type_file(source_file):
        yield from _parse_type_signatures(content)
    else:
        yield from _parse_function_signatures(content)


def _strip_line_comments(content: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in content.splitlines())


def _is_type_file(source_file: Path) -> bool:
    return TYPES_FOLDER_NAME in source_file.parts


def _parse_function_signatures(content: str) -> Iterable[Signature]:
    pattern = re.compile(
        r"(?m)^\s*(?P<kind>meta-fn|fn)\s+"
        r"(?P<name>@?[\w-]+)\s*"
        r"\((?P<args>[^)]*)\)\s*"
        r"(?P<type>@?[\w\[\]-]+)?\s*\{"
    )
    for match in pattern.finditer(content):
        kind = "meta-function" if match.group("kind") == "meta-fn" else "function"
        yield Signature(
            name=match.group("name"),
            kind=kind,
            type=match.group("type") or "void",
            arguments=_parse_arguments(match.group("args")),
        )


def _parse_type_signatures(content: str) -> Iterable[Signature]:
    type_pattern = re.compile(r"(?m)^\s*type\s+(?P<name>@?[\w-]+)\s*")
    for match in type_pattern.finditer(content):
        name = match.group("name")
        cursor = match.end()
        suffix = content[cursor:].lstrip()

        if suffix.startswith(":"):
            alias_match = re.match(r":\s*(?P<type>@?[\w\[\]-]+)", suffix)
            if alias_match:
                yield Signature(name=name, kind="alias", type=alias_match.group("type"))
            continue

        if suffix.startswith("{"):
            body = _read_braced_body(suffix)
            fields = _parse_arguments(body)
            if fields:
                yield Signature(name=name, kind="struct", members=fields)
            else:
                yield Signature(name=name, kind="enum", variants=_parse_variants(body))


def _read_braced_body(text: str) -> str:
    depth = 0
    start = None
    for index, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = index + 1
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:index]
    return ""


def _parse_arguments(raw_args: str) -> tuple[ArgumentSignature, ...]:
    args: list[ArgumentSignature] = []
    for token in re.findall(r"@?[\w-]+\s*:\s*@?[\w\[\]-]+", raw_args):
        name, type_name = token.split(":", 1)
        args.append(ArgumentSignature(name=name.strip(), type=type_name.strip()))
    return tuple(args)


def _parse_variants(raw_body: str) -> tuple[str, ...]:
    return tuple(re.findall(r"@?[\w-]+", re.sub(r"\{[^}]*\}", "", raw_body)))


def _doc_path_for(project_path: Path, source_file: Path) -> Path:
    relative = source_file.relative_to(project_path / SOURCE_FOLDER_NAME)
    return project_path / DOCS_FOLDER_NAME / Path(str(relative) + ".md")


def _write_doc_signatures(doc_file: Path, signatures: tuple[Signature, ...]) -> None:
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    title = doc_file.name.removesuffix(".hat.md").removesuffix(".md")
    existing = doc_file.read_text() if doc_file.exists() else f"# {title}\n\n"
    generated = _render_generated_section(signatures)

    pattern = re.compile(rf"{re.escape(AUTO_START)}.*?{re.escape(AUTO_END)}", re.DOTALL)
    if pattern.search(existing):
        updated = pattern.sub(generated.strip(), existing)
    else:
        updated = existing.rstrip() + "\n\n" + generated

    doc_file.write_text(updated.rstrip() + "\n")


def _render_generated_section(signatures: tuple[Signature, ...]) -> str:
    lines = [
        AUTO_START,
        "## Signatures",
        "",
        "> This section is managed by `hat update`. Edit the Documentation sections below it.",
        "",
    ]

    if not signatures:
        lines.extend(["No H-hat signatures found.", ""])
    for signature in signatures:
        lines.extend(_render_signature(signature))

    lines.append(AUTO_END)
    lines.append("")
    return "\n".join(lines)


def _render_signature(signature: Signature) -> list[str]:
    lines = [
        f"### {signature.name}",
        "",
        "- Signature:",
        f"  - Name: {signature.name}",
        f"  - Kind: {signature.kind}",
        f"  - Paradigm: {signature.paradigm}",
    ]
    if signature.type:
        lines.append(f"  - Type: {signature.type}")

    if signature.arguments:
        lines.extend(["  - Arguments:", "", "    | Argument | Type | Paradigm |"])
        lines.append("    | :--- | :--- | :--- |")
        for arg in signature.arguments:
            lines.append(f"    | {arg.name} | {arg.type} | {arg.paradigm} |")
    if signature.members:
        lines.extend(["  - Members/Fields:", "", "    | Member/Field | Type | Paradigm |"])
        lines.append("    | :--- | :--- | :--- |")
        for member in signature.members:
            lines.append(f"    | {member.name} | {member.type} | {member.paradigm} |")
    if signature.variants:
        lines.extend(["  - Variants:", ""])
        for variant in signature.variants:
            lines.append(f"    - {variant}")

    lines.extend(["", "#### Documentation", "", ""])
    return lines


def _paradigm_for(*parts: str) -> str:
    return "quantum" if any(part.startswith("@") for part in parts) else "classical"
