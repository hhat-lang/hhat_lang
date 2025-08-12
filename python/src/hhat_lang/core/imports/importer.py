from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, cast, Callable

from hhat_lang.core.code.new_ir import BaseIR, IRGraph, IRHash
from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.data.fn_def import BaseFnKey, BaseFnCheck, FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.toolchain.project import SOURCE_TYPES_PATH, SOURCE_FOLDER_NAME


class BaseImporter(ABC):
    _base: Path
    _project_root: Path
    _parser_fn: Callable[[str, Path, IRGraph], BaseIR]
    _ir_graph: IRGraph

    def __init__(
        self,
        project_root: Path,
        parser_fn: Callable[[str, Path, IRGraph], BaseIR],
        ir_graph: IRGraph,
    ) -> None:
        self._project_root = project_root
        self._parser_fn = parser_fn
        self._ir_graph = ir_graph

    @property
    def base(self) -> Path:
        return self._base

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def parser_fn(self) -> Callable[[str, Path, IRGraph], BaseIR]:
        return self._parser_fn

    @property
    def ir_graph(self) -> IRGraph:
        return self._ir_graph

    @classmethod
    def _path_parts(cls, name: CompositeSymbol) -> tuple[tuple[str, ...], str, Symbol]:
        parts = tuple(name.value)

        if len(parts) == 1:
            dirs: tuple[str, ...] = ()
            file_name = parts[0]
            importer_name = parts[0]

        else:
            dirs = parts[:-2]
            file_name = parts[-2]
            importer_name = parts[-1]

        return dirs, file_name, Symbol(importer_name)


class TypeImporter(BaseImporter):
    """Locate and load types under ``src/hat_types`` relative to a project.

    Each ``.hat`` file is scanned for ``type`` declarations and
    ``use(type:...)`` statements. Referenced types are resolved recursively.
    Circular imports are tolerated during discovery, but a missing type raises
    ``FileNotFoundError`` or ``ValueError``.
    """

    cached_types: dict[Symbol | CompositeSymbol, BaseTypeDataStructure] = dict()

    def __init__(self, project_root: Path, parser_fn: Callable, ir_graph: IRGraph):
        self._base = Path(project_root).resolve() / SOURCE_TYPES_PATH
        super().__init__(project_root, parser_fn, ir_graph)

    def _check_type(
        self,
        name: Symbol | CompositeSymbol,
        # path_base: Path,
        # project_root: Path,
        # parser_fn: Callable[[str, Path, IRGraph], BaseIR],
    ) -> IRHash:  # BaseTypeDataStructure:
        """

        Args:
            name:

        Returns:
        """

        dir_name, file_name, type_name = self._path_parts(name)

        if (Path(*dir_name, file_name), type_name) not in self.ir_graph.nodes:
            pass

        # """
        # Check the type name (as ``Symbol`` or ``CompositeSymbol``) and retrieves it
        # from the cached types or parse its file to retrieve it. It will cache all
        # the other types for future reference to avoid duplicate parsing in the same
        # files.
        #
        # Args:
        #     name: the type name as ``Symbol`` or ``CompositeSymbol``
        #     path_base:
        #     project_root:
        #     parser_fn: the parse function that contains the visitor function for a
        #         defined ``ParserIRVisitor`` instance
        #     ir_graph: the ``IRGraph`` instance
        #
        # Returns:
        #     The type container data
        # """
        #
        # dirs, file_name, type_name = cls._path_parts(name)
        # file_path = path_base.joinpath(*dirs, file_name + ".hat")
        # cached_container = cls.cached_types.get(name, None)
        #
        # if cached_container:
        #     return cached_container
        #
        # raw_code = file_path.read_text()
        # program = parser_fn(raw_code, project_root, ir_graph)
        #
        # type_container = program.types.table.get(Symbol(type_name), None)
        #
        # if type_container:
        #     cls.cached_types.update({k: v for k, v in program.types.table.items()})
        #     return type_container
        #
        # raise FileNotFoundError(file_path)

    def import_types(
        self,
        names: Iterable[CompositeSymbol],
    ) -> dict[Symbol | CompositeSymbol, BaseTypeDataStructure]:
        return {name: self._check_type(name) for name in names}


class FnImporter(BaseImporter):
    cached_fns: dict[Symbol | CompositeSymbol, dict[BaseFnKey, FnDef]] = dict()

    def __init__(self, project_root: Path, parser_fn: Callable):
        self._base = Path(project_root).resolve() / SOURCE_FOLDER_NAME
        super().__init__(project_root, parser_fn)

    @classmethod
    def _check_fn(
        cls,
        name: CompositeSymbol,
        path_base: Path,
        project_root: Path,
        parser_fn: Callable[[str, Path, IRGraph], BaseIR],
        ir_graph: IRGraph,
    ) -> dict[BaseFnKey, FnDef]:
        dirs, file_name, fn_name = cls._path_parts(name)
        file_path = path_base.joinpath(*dirs, file_name + ".hat")
        cached_container = cls.cached_fns.get(name, None)

        if cached_container:
            return cached_container

        raw_code = file_path.read_text()
        program = parser_fn(raw_code, project_root, ir_graph)

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
        self,
        names: Iterable[Symbol | CompositeSymbol],
        ir_graph: IRGraph,
    ) -> dict[Symbol | CompositeSymbol, dict[BaseFnKey, FnDef]]:
        for name in names:
            self._check_fn(
                name, self._base, self.project_root, self.parser_fn, ir_graph
            )

        return self.cached_fns
