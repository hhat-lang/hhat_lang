from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, cast, Callable

from hhat_lang.core.code.new_ir import BaseIR
from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.data.core import Symbol, CompositeSymbol
# from hhat_lang.dialects.heather.code.ast import (
#     CompositeId,
#     CompositeIdWithClosure,
#     Id,
#     Imports,
#     TypeDef,
#     TypeImport,
# )
from hhat_lang.core.data.fn_def import BaseFnKey, BaseFnCheck, FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure

# from hhat_lang.dialects.heather.parsing.ir_visitor import parse

_PARSE_CACHE: dict[Path, tuple[float, list[str], list[CompositeSymbol]]] = {}
_TYPE_CACHE: dict[Path, BaseTypeDataStructure] = {}


def _id_parts(obj: Symbol | CompositeSymbol) -> list[str]:
    if isinstance(obj, CompositeSymbol):
        return [p.value[0] for p in obj]
    return [cast(str, obj.value[0])]


def _expand_group_closures(raw: str) -> str:
    """Rewrite grouped closures to many-import form for the parser."""

    token = r"@?[A-Za-z][A-Za-z0-9_-]*"
    prefix_re = re.compile(rf"({token}(?:\.{token})*)\.{{")

    def _split_tokens(inner: str) -> list[str]:
        tokens: list[str] = []
        buf: list[str] = []
        depth = 0
        for ch in inner.strip():
            if ch.isspace() and depth == 0:
                if buf:
                    tokens.append("".join(buf))
                    buf = []
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            buf.append(ch)
        if buf:
            tokens.append("".join(buf))
        return tokens

    result: list[str] = []
    i = 0
    depth = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "[":
            depth += 1
            result.append(ch)
            i += 1
            continue
        if ch == "]":
            depth -= 1
            result.append(ch)
            i += 1
            continue

        m = prefix_re.match(raw, i)
        if not m:
            result.append(ch)
            i += 1
            continue

        base = m.group(1)
        j = m.end()
        brace_depth = 1
        start = j
        while j < len(raw) and brace_depth:
            if raw[j] == "{":
                brace_depth += 1
            elif raw[j] == "}":
                brace_depth -= 1
            j += 1
        inner = raw[start : j - 1]
        parts = _split_tokens(inner)
        if len(parts) <= 1:
            result.append(raw[i:j])
        else:
            expanded = " ".join(f"{base}.{p}" for p in parts)
            if depth > 0:
                result.append(expanded)
            else:
                result.append(f"[{expanded}]")
        i = j

    return "".join(result)


# def _parse_file(
#     file_path: Path,
#     project_root: Path,
#     parser: Callable[[str, Path], BaseIR]
# ) -> tuple[list[str], list[CompositeSymbol]]:
#     mtime = file_path.stat().st_mtime
#     cached = _PARSE_CACHE.get(file_path)
#     if cached and cached[0] == mtime:
#         return cached[1], cached[2]
#
#     raw_code = file_path.read_text()
#     # expanded = _expand_group_closures(raw_code)
#     # program = parse(expanded)
#     program = parser(raw_code, project_root)
#
#     imports: list[CompositeSymbol] = []
#     names: list[str] = []
#
#     imports_node: BaseImports | None = None
#     defs_tuple: tuple = ()
#
#     if program.types is not None:
#         for type_content in program.types.table.values():
#             defs_tuple += type_content,
#
#     #
#     # if len(program.types) == 2:
#     #     first, second = values
#     #     if isinstance(first, BaseImports):
#     #         imports_node = first
#     #         if isinstance(second, tuple):
#     #             defs_tuple = tuple(d for d in second if isinstance(d, Mapping))
#     #     else:
#     #         if isinstance(first, tuple):
#     #             defs_tuple = tuple(d for d in first if isinstance(d, Mapping))
#     #         if isinstance(second, BaseImports):
#     #             imports_node = second
#     # elif len(values) == 1:
#     #     item = values[0]
#     #     if isinstance(item, BaseImports):
#     #         imports_node = item
#     #     elif isinstance(item, tuple):
#     #         defs_tuple = tuple(d for d in item if isinstance(d, Mapping))
#
#     def collect(
#         obj: Symbol | CompositeSymbol | BaseIRBlock,
#         prefix: tuple[str, ...] = (),
#     ) -> list[CompositeSymbol]:
#         if isinstance(obj, BaseIRBlock):
#             name_ast, values = obj.args
#             base = prefix + tuple(_id_parts(cast(Symbol | CompositeSymbol, name_ast)))
#             res: list[CompositeSymbol] = []
#             for v in list(values):  # type: ignore[arg-type]
#                 res.extend(
#                     collect(cast(Symbol | CompositeSymbol | BaseIRBlock, v), base)
#                 )
#             return res
#         if isinstance(obj, CompositeSymbol):
#             return [CompositeSymbol(prefix + tuple(_id_parts(obj)))]
#         return [CompositeSymbol(prefix + (cast(str, obj.value[0]),))]
#
#     if imports_node:
#         for imp in cast(tuple[TypeImport, ...], imports_node.value[0]):
#             for t in cast(
#                 tuple[Symbol | CompositeSymbol | BaseIRBlock, ...], imp.value
#             ):
#                 imports.extend(collect(t))
#
#     for d in defs_tuple:
#         parts = _id_parts(cast(Symbol | CompositeSymbol, d.value[0]))
#         names.append(parts[-1])
#
#     _PARSE_CACHE[file_path] = (mtime, names, imports)
#     return names, imports


# def _parse_type_names(
#     file_path: Path,
#     project_root: Path,
#     parser: Callable
# ) -> list[str]:
#     return _parse_file(file_path, project_root, parser)[0]
#
#
# def _parse_type_imports(
#     file_path: Path,
#     project_root: Path,
#     parser: Callable
# ) -> list[CompositeSymbol]:
#     return _parse_file(file_path, project_root, parser)[1]


# def _check_files(
#     type_path: Path,
#     project_root: Path,
#     parser: Callable[[str, Path], BaseIR]
# ) -> dict[Symbol | CompositeSymbol, BaseTypeDataStructure]:
#     type_checked = _TYPE_CACHE.get(type_path)
#
#     if type_checked:
#         type_path_str = tuple(str(type_path).strip("/").split("/"))
#         return {CompositeSymbol(type_path): type_checked}
#
#     raw_code = type_path.read_text()
#     program = parser(raw_code, project_root)
#
#     return program.types.table


class BaseImporter(ABC):
    _base: Path

    def __init__(self, project_root: Path, parser_fn: Callable) -> None:
        self._project_root = project_root
        self._parser_fn = parser_fn
        self._loaded: dict[CompositeSymbol, Path] = {}
        self._processing: set[CompositeSymbol] = set()

    @property
    def base(self) -> Path:
        return self._base

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def parser_fn(self) -> Callable:
        return self._parser_fn

    @classmethod
    def _path_parts(cls, name: CompositeSymbol) -> tuple[list[str], str, str]:
        parts = list(name.value)

        if len(parts) == 1:
            dirs: list[str] = []
            file_name = parts[0]
            importer_name = parts[0]

        else:
            dirs = parts[:-2]
            file_name = parts[-2]
            importer_name = parts[-1]

        return dirs, file_name, importer_name


class TypeImporter(BaseImporter):
    """Locate and load types under ``src/hat_types`` relative to a project.

    Each ``.hat`` file is scanned for ``type`` declarations and
    ``use(type:...)`` statements. Referenced types are resolved recursively.
    Circular imports are tolerated during discovery, but a missing type raises
    ``FileNotFoundError`` or ``ValueError``.
    """

    cached_types: dict[Symbol | CompositeSymbol, BaseTypeDataStructure] = dict()

    def __init__(self, project_root: Path, parser_fn: Callable):
        self._base = Path(project_root).resolve() / "src" / "hat_types"
        super().__init__(project_root, parser_fn)

    @classmethod
    def _check_type(
        cls,
        name: Symbol | CompositeSymbol,
        path_base: Path,
        project_root: Path,
        parser_fn: Callable[[str, Path], BaseIR]
    ) -> BaseTypeDataStructure:
        """
        Check the type name (as ``Symbol`` or ``CompositeSymbol``) and retrieves it
        from the cached types or parse its file to retrieve it. It will cache all
        the other types for future reference to avoid duplicate parsing in the same
        files.

        Args:
            name: the type name as ``Symbol`` or ``CompositeSymbol``
            parser_fn:

        Returns:
            The type container data
        """

        dirs, file_name, type_name = cls._path_parts(name)
        file_path = path_base.joinpath(*dirs, file_name + ".hat")
        cached_container = cls.cached_types.get(name, None)

        if cached_container:
            return cached_container

        raw_code = file_path.read_text()
        program = parser_fn(raw_code, project_root)

        type_container = program.types.table.get(Symbol(type_name), None)

        if type_container:
            cls.cached_types.update({k: v for k, v in program.types.table.items()})
            return type_container

        raise FileNotFoundError(file_path)

    # def _discover(self, name: CompositeSymbol) -> None:
    #     if name in self._loaded or name in self._processing:
    #         return
    #
    #     self._processing.add(name)
    #     try:
    #         dirs, file_name, type_name = self._path_parts(name)
    #         file_path = self._base.joinpath(*dirs, file_name + ".hat")
    #
    #         if not file_path.exists():
    #             raise FileNotFoundError(file_path)
    #
    #         defined, imports = _parse_file(file_path, self.project_root, self.parser)
    #         # defined = _parse_type_names(file_path, self.project_root, self.parser)
    #         print(f"{defined=} | {imports=}")
    #         if type_name not in defined:
    #             raise ValueError(f"Type '{type_name}' not found in {file_path}")
    #
    #         self._loaded[name] = file_path
    #
    #         for imp in imports:  # _parse_type_imports(file_path, self.project_root, self.parser):
    #             self._discover(imp)
    #     finally:
    #         self._processing.remove(name)

    def import_types(
        self, names: Iterable[CompositeSymbol]
    ) -> dict[Symbol | CompositeSymbol, BaseTypeDataStructure]:  # dict[CompositeSymbol, Path]:
        # for name in names:
        #     self._discover(name)
        # return dict(self._loaded)

        return {
            name: TypeImporter._check_type(name, self._base, self.project_root, self.parser_fn)
            for name in names
        }


class FnImporter(BaseImporter):
    cached_fns: dict[Symbol | CompositeSymbol, dict[BaseFnKey, FnDef]] = dict()

    def __init__(self, project_root: Path, parser_fn: Callable):
        self._base = Path(project_root).resolve() / "src"
        super().__init__(project_root, parser_fn)

    @classmethod
    def _check_fn(
        cls,
        name: CompositeSymbol,
        path_base: Path,
        project_root: Path,
        parser_fn: Callable[[str, Path], BaseIR]
    ) -> dict[BaseFnKey, FnDef]:
        dirs, file_name, fn_name = cls._path_parts(name)
        file_path = path_base.joinpath(*dirs, file_name + ".hat")
        cached_container = cls.cached_fns.get(name, None)

        if cached_container:
            return cached_container

        raw_code = file_path.read_text()
        program = parser_fn(raw_code, project_root)

        fn_container = program.fns.table.get(Symbol(fn_name), None)

        if fn_container:
            if isinstance(fn_container, dict):
                for k, v in program.fns.table.items():
                    if k not in cls.cached_fns:
                        cls.cached_fns.update({k: v})

                    else:
                        cls.cached_fns[k].update(v)

            return fn_container

        raise FileNotFoundError(file_path)

    def import_fns(
        self, names: Iterable[Symbol | CompositeSymbol]
    ) -> dict[Symbol | CompositeSymbol, dict[BaseFnKey, FnDef]]:
        for name in names:
            FnImporter._check_fn(name, self._base, self.project_root, self.parser_fn)

        return self.cached_fns
