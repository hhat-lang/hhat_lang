from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Callable, Iterable

from arpeggio import ParserPython
from arpeggio.cleanpeg import ParserPEG

from hhat_lang.core.code.abstract import BaseIR
from hhat_lang.core.code.base import FnHeader
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.fns.core import builtin_fns_path
from hhat_lang.toolchain.project import SOURCE_FOLDER_NAME, SOURCE_TYPES_PATH


class BaseImporter(ABC):
    _base: Path
    _project_root: Path
    _parser_fn: Callable[
        [
            Callable[[Callable], ParserPEG | ParserPython],
            Callable,
            str,
            Path,
            Path,
            IRGraph,
        ],
        BaseIR,
    ]
    _grammar_parser: Callable[[Callable], ParserPEG | ParserPython]
    _program_rule: Callable

    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable[
            [
                Callable[[Callable], ParserPEG | ParserPython],
                Callable,
                str,
                Path,
                Path,
                IRGraph,
            ],
            BaseIR,
        ],
    ) -> None:
        self._project_root = project_root
        self._grammar_parser = grammar_parser
        self._parser_fn = parser_fn
        self._program_rule = program_rule

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def grammar_parser(self) -> Callable[[Callable], ParserPEG | ParserPython]:
        return self._grammar_parser

    @property
    def program_rule(self) -> Callable:
        return self._program_rule

    @property
    def parser_fn(
        self,
    ) -> Callable[
        [
            Callable[[Callable], ParserPEG | ParserPython],
            Callable,
            str,
            Path,
            Path,
            IRGraph,
        ],
        BaseIR,
    ]:
        return self._parser_fn

    @classmethod
    def _path_parts(cls, name: CompositeSymbol) -> tuple[tuple[str, ...], str, Symbol]:
        parts = tuple(name.value)

        if len(parts) == 1:
            # core built-in code
            dirs: tuple[str, ...] = ()
            file_name = "core"
            importer_name = parts[0]

        else:
            dirs = tuple(k.value for k in parts[:-2])
            file_name = parts[-2].value
            importer_name = parts[-1]

        return dirs, file_name, importer_name

    def _get_module_path(self, *path: Path | str) -> Path:
        if len(path) == 1 and path == Path("core.hat"):
            return path[0]

        return Path().joinpath(self._base, *path[:-1], str(path[-1]) + ".hat")

    def _add_module(self, module_path: Path, ir_graph: IRGraph) -> None:
        """To add a new IR module to the graph based on the ``module_path``"""
        raw_code: str = module_path.read_text()
        self._parser_fn(
            self._grammar_parser,
            self._program_rule,
            raw_code,
            self._project_root,
            module_path,
            ir_graph,
        )


class ConstImporter(BaseImporter):
    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable,
    ):
        self._base = Path(project_root).resolve() / SOURCE_FOLDER_NAME
        super().__init__(project_root, grammar_parser, program_rule, parser_fn)

    def _retrieve_const_reference(self):
        pass

    def import_consts(self):
        pass


class TypeImporter(BaseImporter):
    """Locate and load types under ``src/hat_types`` relative to a project.

    Each ``.hat`` file is scanned for ``type`` declarations and
    ``use(type:...)`` statements. Referenced types are resolved recursively.
    Circular imports are tolerated during discovery, but a missing type raises
    ``FileNotFoundError`` or ``ValueError``.
    """

    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable,
    ):
        self._base = Path(project_root).resolve() / SOURCE_TYPES_PATH
        super().__init__(project_root, grammar_parser, program_rule, parser_fn)

    def _retrieve_type_reference(
        self,
        name: CompositeSymbol,
        ir_graph: IRGraph,
    ) -> tuple[Symbol, Path]:
        """
        Retrieve type references to be filled at the node's ``RefTypeTable``.

        Args:
            name: the type path as ``CompositeSymbol``
            ir_graph: the ``IRGraph`` instance

        Returns:
            A tuple with the type name and its module file path
        """

        dir_name, file_name, type_name = self._path_parts(name)
        module_path: Path = self._get_module_path(*dir_name, file_name)

        if module_path not in ir_graph:
            self._add_module(module_path, ir_graph)

        return type_name, module_path

    def import_types(
        self,
        names: Iterable[CompositeSymbol],
        ir_graph: IRGraph,
    ) -> dict[Symbol, Path]:
        return dict(self._retrieve_type_reference(name, ir_graph) for name in names)


class FnImporter(BaseImporter):
    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable,
    ):
        self._base = Path(project_root).resolve() / SOURCE_FOLDER_NAME
        super().__init__(project_root, grammar_parser, program_rule, parser_fn)

    def _retrieve_fn_reference(
        self,
        name: CompositeSymbol,
        ir_graph: IRGraph,
    ) -> tuple[tuple[FnHeader, Path], ...]:
        """
        Retrieve function references to be filled at the node's ``RefFnTable``.

        Args:
            name: the type path as ``CompositeSymbol``
            ir_graph: the ``IRGraph`` instance

        Returns:
            Tuple of tuple-pairs containing the function check object and the module file path
        """

        # TODO: fix it as described below
        #   - for project-defined functions, include only project name and folders
        #       inside 'src' at the module path, like: "project/src/some_folder/some_file.hat"
        #   - for external functions:
        #       - core functions should be at "project/src/.hat_core/core.hat"
        #       - other modules, such as 'math', like "project/stc/.hat_std/math/other_file.hat"
        #   - built-in functions, types, etc should be only imported as the last step when
        #       building the ir graph

        module_path: Path
        dir_name, file_name, fn_name = self._path_parts(name)

        # module_path = Path(*dir_name) / (file_name + ".hat")
        # if module_path in builtin_fns_path:
        #     return tuple(
        #         (fn.fn_header, module_path) for fn in builtin_fns_path[module_path]
        #     )

        module_path = self._get_module_path(*dir_name, file_name)
        if module_path not in ir_graph:
            self._add_module(module_path, ir_graph)

        fns = ir_graph.get_fns(module_path, fn_name)
        return tuple((fn, module_path) for fn in fns)

    def import_fns(
        self,
        names: Iterable[CompositeSymbol],
        ir_graph: IRGraph,
    ) -> dict[FnHeader, Path]:
        res: tuple | tuple[tuple[FnHeader, Path]] = ()

        for name in names:
            res += self._retrieve_fn_reference(name, ir_graph)

        return dict(res)


class ModifierImporter(BaseImporter):
    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable,
    ):
        self._base = Path(project_root).resolve() / SOURCE_FOLDER_NAME
        super().__init__(project_root, grammar_parser, program_rule, parser_fn)

    def _retrieve_modifier_reference(self):
        pass

    def import_modifiers(self):
        pass


class MetaModImporter(BaseImporter):
    def __init__(
        self,
        project_root: Path,
        grammar_parser: Callable[[Callable], ParserPEG | ParserPython],
        program_rule: Callable,
        parser_fn: Callable,
    ):
        self._base = Path(project_root).resolve() / SOURCE_FOLDER_NAME
        super().__init__(project_root, grammar_parser, program_rule, parser_fn)

    def _retrieve_metamod_reference(self):
        pass

    def import_metamods(self):
        pass
