"""Attempt to parse directly to IR"""

from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any, Callable, Iterable

from arpeggio import (
    NonTerminal,
    ParserPython,
    PTNodeVisitor,
    SemanticActionResults,
    Terminal,
    visit_parse_tree,
)
from typing_extensions import deprecated

from hhat_lang.core.code.base import FnHeader
from hhat_lang.core.code.ir_block import (
    IRBlock,
    IRInstr,
)
from hhat_lang.core.code.ir_custom import (
    ArgsBlock,
    ArgsValuesBlock,
    BodyBlock,
    ModifierArgsBlock,
    ModifierBlock,
    OptionBlock,
    ReturnBlock,
)
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Literal,
    LiteralArray,
    ObjArray,
    Pointer,
    Reference,
    SimpleObj,
    Symbol,
)
from hhat_lang.core.data.fn_def import BuiltinFnDef, FnDef
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.imports import TypeImporter
from hhat_lang.core.imports.importer import FnImporter
from hhat_lang.core.types.abstract_base import BaseTypeDef, QSize, Size
from hhat_lang.core.types.builtin_types import builtins_types
from hhat_lang.core.types.core import EnumTypeDef, SingleTypeDef, StructTypeDef
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import (
    IR,
    AssignInstr,
    CallInstr,
    CastInstr,
    DeclareAssignInstr,
    DeclareInstr,
)
from hhat_lang.dialects.heather.code.simple_ir_builder.ir_builder import build_ir
from hhat_lang.dialects.heather.grammar import WHITESPACE
from hhat_lang.dialects.heather.grammar.fn_grammar import fn_program
from hhat_lang.dialects.heather.grammar.generic_grammar import comment
from hhat_lang.dialects.heather.grammar.type_grammar import type_program
from hhat_lang.dialects.heather.parsing.utils import FnsDict, ImportDicts, TypesDict

#########################


def read_grammar() -> str:
    grammar_path = Path(__file__).parent.parent / "grammar" / "grammar.peg"

    if grammar_path.exists():
        return open(grammar_path, "r").read()

    raise ValueError("No grammar found on the grammar directory.")


############################
# PARSING WITH PYTHON CODE #
############################


def parser_grammar_code(program_fn: Callable) -> ParserPython:
    """

    Args:
        program_fn: the function that starts the grammar (probably "<something>_program").

    Returns:
        The ``ParserPython`` constructor
    """

    return ParserPython(
        program_fn, comment_def=comment, ws=WHITESPACE, memoization=True
    )


###################
# PARSER FUNCTION #
###################


def parse(
    grammar_parser: Callable[[Callable], ParserPython],
    program_rule: Callable,
    raw_code: str,
    project_root: Path,
    module_path: Path,
    ir_graph: IRGraph,
) -> IR:
    """
    Used to parse code according to some grammar.

    Args:
        grammar_parser: function like
            ``hhat_lang.dialects.heather.parsing.ir_visitor.parser_grammar_code`` that
            receives a program rule (a function that starts the grammar), and returns a
            ``ParserPython`` instance
        program_rule: the function that starts the grammar (probably ``<something>_program``
        raw_code: the code to be parsed as str
        project_root: ``Path`` object of the project root path
        module_path: ``Path`` object of the current module path
        ir_graph: the project ``IRGraph``

    Returns:
        An ``IR`` instance
    """

    parse_tree = grammar_parser(program_rule).parse(raw_code)
    return visit_parse_tree(
        parse_tree,
        ParserIRVisitor(
            grammar_parser,
            project_root,
            module_path,
            ir_graph,
        ),
    )


###########################
# PARSER IR VISITOR CLASS #
###########################


class ParserIRVisitor(PTNodeVisitor):
    """Visitor for parsing using IR code logic instead of AST's"""

    # TODO: split the ParserIRVisitor class for different grammars

    _root: Path
    _module_path: Path
    _ir_graph: IRGraph
    _grammar: Callable[[Callable], ParserPython]

    def __init__(
        self,
        grammar_parser: Callable[[Callable], ParserPython],
        project_root: Path,
        module_path: Path,
        ir_graph: IRGraph,
    ):
        super().__init__()
        self._grammar = grammar_parser
        self._root = project_root
        self._module_path = module_path
        self._ir_graph = ir_graph

    @property
    def grammar(self) -> Callable[[Callable], ParserPython]:
        return self._grammar

    @property
    def project_root(self) -> Path:
        return self._root

    @property
    def module_path(self) -> Path:
        return self._module_path

    @property
    def ir_graph(self) -> IRGraph:
        return self._ir_graph

    def visit_type_program(self, _: NonTerminal, child: SemanticActionResults) -> IR:
        refs: dict[Symbol | CompositeSymbol, Path] = dict()
        types: tuple[BaseTypeDef, ...] | tuple = ()

        for k in child:
            match k:
                case ImportDicts():
                    refs.update(k.types)

                case BaseTypeDef():
                    types += (k,)

                case _:
                    print(f"[type-program] ?? {type(k)}")

        visited_ir = build_ir(
            path=self._module_path,
            ref_types=refs,
            ref_fns=dict(),
            types=types,
            fns=(),
            main=None,
        )

        self._ir_graph.add_node(visited_ir)

        return visited_ir

    def visit_fn_program(self, _: NonTerminal, child: SemanticActionResults) -> IR:
        main: BodyBlock | None = None
        ref_types: dict[Symbol | CompositeSymbol, Path] = dict()
        ref_fns: dict[FnHeader, Path] = dict()
        types: tuple[BaseTypeDef, ...] | tuple = ()
        fns: tuple[FnDef | BuiltinFnDef, ...] | tuple = ()

        for k in child:
            match k:
                case IRBlock():
                    if isinstance(k, BodyBlock):
                        main = k

                case ImportDicts():
                    ref_types.update(k.types)
                    ref_fns.update(k.fns)

                case BaseTypeDef():
                    types += (k,)

                case FnDef() | BuiltinFnDef():
                    fns += (k,)

                case _:
                    print(f"[?] unknown child of type {type(k)}")

        visited_ir = build_ir(
            path=self._module_path,
            ref_types=ref_types,
            ref_fns=ref_fns,
            types=types,
            fns=fns,
            main=main,
        )

        if isinstance(main, BodyBlock):
            self._ir_graph.add_main_node(visited_ir)

        else:
            self._ir_graph.add_node(visited_ir)

        return visited_ir

    def visit_type_file(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> BaseTypeDef:
        return child[0]

    def visit_typesingle(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> SingleTypeDef | ErrorHandler:
        # TODO: implement a better resolver to account for custom and circular imports;
        #  for now, just check if it's built-in.

        btype = builtins_types[child[1]]
        single = SingleTypeDef(name=child[0])
        return single.add_member(btype)

    def visit_typemember(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> tuple[Symbol | CompositeSymbol | BaseTypeDef, Symbol | CompositeSymbol]:
        # Fow now, it will try to fetch built-in types, otherwise it will
        # save the check for later
        member_type = builtins_types.get(child[1], child[1])
        member_name = child[0]
        return member_type, member_name

    def visit_typestruct(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> BaseTypeDef:
        struct = StructTypeDef(name=child[0], num_members=len(child[1:]))

        # second, populate struct
        for t, m in child[1:]:
            struct.add_member(t, m)

        return struct

    def visit_enummember(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> Symbol | CompositeSymbol | BaseTypeDef:
        # should have just one
        if len(child) != 1:
            raise ValueError("enum member must be a single attribute")

        return child[0]

    def visit_typeenum(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> BaseTypeDef:
        enum_ds = EnumTypeDef(name=child[0], num_members=len(child[1:]))

        for member in child[1:]:
            enum_ds.add_member(member)

        return enum_ds

    def visit_typeunion(self, _: NonTerminal, child: SemanticActionResults) -> Any:
        raise NotImplementedError()

    def visit_fns(self, _: NonTerminal, child: SemanticActionResults) -> FnDef:
        if len(child) == 4:
            return FnDef(
                fn_name=child[0], fn_args=child[1], fn_type=child[2], fn_body=child[3]
            )

        return FnDef(fn_name=child[0], fn_args=child[1], fn_type=None, fn_body=child[2])

    def visit_fnargs(self, _: NonTerminal, child: SemanticActionResults) -> ArgsBlock:
        return ArgsBlock(*child)

    def visit_argtype(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ArgsValuesBlock:
        return ArgsValuesBlock((child[0], child[1]))

    def visit_fn_body(self, _: NonTerminal, child: SemanticActionResults) -> BodyBlock:
        return BodyBlock(*child)

    def visit_body(self, _: NonTerminal, child: SemanticActionResults) -> BodyBlock:
        values: tuple[IRInstr | IRBlock, ...] | tuple = ()
        for k in child:
            match k:
                case IRInstr():
                    values += (k,)

                case IRBlock():
                    values += (k,)

                case _:
                    print(f"    -> something else: {k} ({type(k)})")

        return BodyBlock(*values)

    def visit_declare(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> DeclareInstr:
        if len(child) == 2:
            return DeclareInstr(var=child[0], var_type=child[1])

        if len(child) == 3:
            return DeclareInstr(
                var=ModifierBlock(obj=child[0], args=child[1]), var_type=child[2]
            )

        raise ValueError("declaring variable must have only variable and its type")

    def visit_assign(self, _: NonTerminal, child: SemanticActionResults) -> AssignInstr:
        return AssignInstr(var=child[0], value=child[1])

    def visit_assign_ds(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> AssignInstr:
        return AssignInstr(var=child[0], value=ArgsBlock(*child[1:]))

    def visit_declareassign(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> DeclareAssignInstr:
        if len(child) == 3:
            return DeclareAssignInstr(var=child[0], var_type=child[1], value=child[2])

        if len(child) == 4:
            return DeclareAssignInstr(
                var=ModifierBlock(obj=child[0], args=child[1]),
                var_type=child[2],
                value=child[3],
            )

        raise ValueError("declaring and assigning cannot contain more than 4 elements")

    def visit_declareassign_ds(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> Any:
        if isinstance(child[1], ModifierArgsBlock):
            return DeclareAssignInstr(
                var=ModifierBlock(obj=child[0], args=child[1]),
                var_type=child[2],
                value=ArgsBlock(*child[3:]) if len(child) > 4 else child[3],
            )

        return DeclareAssignInstr(
            var=child[0], var_type=child[1], value=ArgsBlock(*child[2:])
        )

    def visit_fn_return(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ReturnBlock:
        return ReturnBlock(*child)

    def visit_expr(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> IRBlock | IRInstr | Symbol | CompositeSymbol:
        # returning the child; there should exist only one element
        return child[0]

    def visit_cast(self, _: NonTerminal, child: SemanticActionResults) -> CastInstr:
        return CastInstr(data=child[0], to_type=child[1])

    def visit_call(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> CallInstr | ModifierBlock:
        if len(child) == 1:
            # only the caller is present
            return CallInstr(name=child[0])

        if len(child) == 2:
            # possible cases: trait_id, args, or modifier
            match child[1]:
                # args option
                case ArgsBlock() | ArgsValuesBlock():
                    return CallInstr(name=child[0], args=child[1])

                # modifier option
                case ModifierArgsBlock():
                    return ModifierBlock(obj=CallInstr(name=child[0]), args=child[1])

                # trait_id option
                case Symbol() | CompositeSymbol() | ModifierBlock():
                    raise NotImplementedError("trait not implemented yet")

                case _:
                    raise NotImplementedError("unknown case")

        if len(child) == 3:
            # possible cases: trait_id and args, trait_id and modifier, args and modifier
            match (child[1], child[2]):
                # args and modifier
                case (ArgsBlock() | ArgsValuesBlock(), ModifierArgsBlock()):
                    return ModifierBlock(
                        CallInstr(name=child[0], args=child[1]), args=child[2]
                    )

                # trait and something
                case _:
                    raise NotImplementedError()

        if len(child) == 4:
            # everything together :)
            raise NotImplementedError()

        raise ValueError("call cannot have len 0 or > 4")

    def visit_trait_id(self, _: NonTerminal, child: SemanticActionResults) -> Any:
        raise NotImplementedError()

    def visit_args(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ArgsBlock | ArgsValuesBlock:
        argsvalues: tuple[ArgsValuesBlock, ...] | tuple = ()
        args: tuple[SimpleObj | ObjArray | IRInstr | ModifierBlock] | tuple = ()

        for k in child:
            match k:
                case ArgsValuesBlock():
                    argsvalues += (k,)

                case IRInstr() | ModifierBlock():
                    args += (k,)

                case Symbol() | CompositeSymbol() | Literal() | LiteralArray():
                    args += (k,)

                case _:
                    raise ValueError(f"unexpected value from args ({k}, {type(k)})")

        if len(argsvalues) != 0 and len(args) != 0:
            raise ValueError(
                "arguments in functino call cannot mix key-value pairs with value only"
            )

        if args:
            return ArgsBlock(*args)

        return ArgsValuesBlock(*argsvalues)

    def visit_assignargs(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ArgsValuesBlock:
        if len(child) == 2:
            return ArgsValuesBlock((child[0], child[1]))

        raise ValueError(
            "assigning arg with value cannot have more than an argument and a value"
        )

    def visit_callargs(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ArgsValuesBlock:
        return ArgsValuesBlock((child[0], child[1]))

    def visit_valonly(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> SimpleObj | ObjArray:
        return child[0]

    def visit_option(self, _: NonTerminal, child: SemanticActionResults) -> OptionBlock:
        assert len(child) == 2, "Option grammar must have one option and one block"
        return OptionBlock(option=child[0], block=child[1])

    def visit_call_bdn(self, _: NonTerminal, child: SemanticActionResults) -> CallInstr:
        raise NotImplementedError()

    def visit_call_optbdn(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> CallInstr:
        args: tuple = ()
        body: BodyBlock | None = None
        option: tuple[OptionBlock] | tuple = ()

        for k in child[1:]:
            match k:
                case ArgsBlock() | ArgsValuesBlock():
                    args += (k,)

                case BodyBlock():
                    body = k

                case OptionBlock():
                    option += (k,)

                case _:
                    raise ValueError(
                        f"unexpected value on call with body options {k} ({type(k)})"
                    )

        body = BodyBlock(*option) if option else body
        args_entry = ArgsBlock(*args) if args else None
        return CallInstr(name=child[0], args=args_entry, body=body)

    def visit_call_optn(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> CallInstr:
        return CallInstr(name=child[0], option=child[1])

    def visit_id_composite_value(
        self, node: NonTerminal, child: SemanticActionResults
    ) -> CompositeSymbol | tuple:
        # Id composite value should have only one value
        return child[0]

    def visit_imports(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ImportDicts:
        types = TypesDict()
        fns = FnsDict()

        for k in child:
            match k:
                case TypesDict():
                    types.update(k)

                case FnsDict():
                    fns.update(k)

        parsed_imports = ImportDicts(types=types, fns=fns)
        return parsed_imports

    def visit_typeimport(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> TypesDict:
        if isinstance(child[0], tuple):
            types = TypesDict()
            importer = TypeImporter(self._root, self._grammar, type_program, parse)
            res = importer.import_types(child[0], self._ir_graph)

            for k, v in res.items():
                types[k] = v

            return types

        raise ValueError("type import not tuple?")

    def visit_fnimport(self, _: NonTerminal, child: SemanticActionResults) -> FnsDict:
        if isinstance(child[0], tuple):
            fns = FnsDict()
            importer = FnImporter(self._root, self._grammar, fn_program, parse)
            res = importer.import_fns(child[0], self._ir_graph)

            for k, v in res.items():
                fns[k] = v

            return fns

        raise ValueError("fn import no tuple?")

    def visit_single_import(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> tuple[Symbol | CompositeSymbol] | tuple:
        if len(child) > 1:
            raise ValueError("single import cannot contain more than one import")

        return child[0] if isinstance(child[0], tuple) else (child[0],)

    def visit_many_import(self, _: NonTerminal, child: SemanticActionResults) -> tuple:
        return tuple(chain.from_iterable(child))

    def visit_main(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> IRBlock | tuple:
        if len(child) == 0:
            return ()

        return BodyBlock(*child)

    def visit_composite_id_with_closure(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> tuple[CompositeSymbol, ...] | tuple:
        _root: tuple[Symbol, ...] = ()

        match parent_id := child[0]:
            case Symbol():
                _root = (parent_id,)

            case CompositeSymbol():
                _root = parent_id.value

            case _:
                raise ValueError(
                    f"something went wrong on composite id with closure {parent_id} ({type(parent_id)})"
                )

        def _compose_id_group(
            data: Iterable[Symbol | tuple | list | CompositeSymbol],
        ) -> tuple[tuple[Symbol, ...], ...]:
            ids = ()

            for p in data:
                match p:
                    case Symbol():
                        ids += ((p,),)

                    case CompositeSymbol():
                        ids += (p.value,)

                    case tuple() | list():
                        ids += _compose_id_group(p)

                    case _:
                        raise ValueError(
                            f"unexpected composite id children {p} ({type(p)})"
                        )

            return ids

        res: tuple[tuple[Symbol, ...], ...] = _compose_id_group(child[1:])
        final_ids: tuple[CompositeSymbol, ...] = tuple(
            CompositeSymbol(_root + k) for k in res
        )
        return final_ids

    def visit_full_id(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> Symbol | CompositeSymbol | ModifierBlock:
        if len(child) == 1:
            return child[0]

        if len(child) == 2:
            return ModifierBlock(obj=child[0], args=child[1])

        raise NotImplementedError("symbol with modifier not implemented yet")

    def visit_modifier(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> ModifierArgsBlock:
        return ModifierArgsBlock(tuple(k for k in child))

    def visit_array(self, _: NonTerminal, child: SemanticActionResults) -> ObjArray:
        raise NotImplementedError("array not implemented yet")

    def visit_composite_id(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> CompositeSymbol:
        return CompositeSymbol(value=_resolve_data_to_symbol(child))

    def visit_simple_id(self, node: Terminal, _: None) -> Symbol:
        return Symbol(value=node.value)

    def visit_ref(self, node: Terminal, _: None) -> Symbol:
        return Reference(value=node.value)

    def visit_pointer(self, node: Terminal, _: None) -> Symbol:
        return Pointer(value=node.value)

    def visit_literal(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> Literal | LiteralArray:
        if len(child) == 1:
            return child[0]

        if len(child) == 2:
            if isinstance(child[0], Literal) and isinstance(
                child[1], Symbol | CompositeSymbol
            ):
                return Literal(value=child[0].value, lit_type=child[1])

        raise ValueError(f"unknown literal {child}")

    def visit_complex(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> LiteralArray:
        raise NotImplementedError("complex type not implemented yet")

    def visit_t_null(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("null"))

    def visit_t_bool(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("bool"))

    def visit_t_str(self, node: NonTerminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("str"))

    def visit_t_int(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("int"))

    def visit_t_float(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("float"))

    def visit_t_imag(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("imag"))

    def visit_qt_bool(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("@bool"))

    def visit_qt_int(self, node: Terminal, _: None) -> Literal:
        return Literal(value=node.value, lit_type=Symbol("@int"))


def _resolve_data_to_symbol(
    data: (
        SemanticActionResults
        | tuple
        | SimpleObj
        | CompositeSymbol
        | ModifierBlock
        | ObjArray
        | str
    ),
) -> tuple | tuple[Symbol | CompositeSymbol, ...]:
    match data:
        case Symbol() | CompositeSymbol():
            return (data,)

        case Literal():
            return (data.type,)

        case LiteralArray():
            return _resolve_data_to_symbol(data.value)

        case ModifierBlock():
            return (data,)

        case SemanticActionResults() | tuple():
            pure_data: tuple | tuple[Symbol, ...] = ()

            for k in data:
                match k:
                    case Symbol() | CompositeSymbol():
                        pure_data += (k,)

                    # case str():
                    #     pure_data += (k,)

                    case LiteralArray():
                        pure_data += k.value

            return pure_data

        # case str():
        #     return (data,)

        case _:
            raise NotImplementedError()


@deprecated("'_fetch_struct_size_qsize' function will be deprecated, don't use it")
def _fetch_struct_size_qsize(
    obj: SemanticActionResults | tuple[Symbol | CompositeSymbol | BaseTypeDef],
) -> tuple[Size | None, QSize | None]:
    """
    Fetch size and qsize attributes for struct data type. If members are not built-in types,
    it will be skipped and be resolved later on, when all the types are defined.

    Args:
        obj: the parser holder of type members

    Returns:
        A tuple of ``size`` and ``qsize``. They can be ``Size`` or ``None``, and
        ``QSize`` or ``None``, respectively.
    """

    count_size = 0
    count_qsize_min = 0
    count_qsize_max = 0

    # first, count the size and qsize
    for member_type, member_name in obj:
        if isinstance(member_type, BaseTypeDef):
            count_size += member_type.size.size
            count_qsize_min += member_type.qsize.min
            count_qsize_max += member_type.qsize.max or 0

    size = Size(count_size) if count_size > 0 else None
    qsize = (
        None
        if count_qsize_min == 0 and count_qsize_max == 0
        else QSize(count_qsize_min, count_qsize_max or None)
    )
    return size, qsize


@deprecated("'_fetch_enum_size_qsize' function will be deprecated soon, don't use it")
def _fetch_enum_size_qsize(
    obj: SemanticActionResults | tuple[Symbol | CompositeSymbol | BaseTypeDef],
) -> tuple[Size | None, QSize | None]:
    """
    Fetch size and qsize attributes for enum data type. If members are not built-in types,
    it will be skipped and be resolved later on, when all the types are defined.

    Args:
        obj: the parser holder of type members

    Returns:
        A tuple of ``size`` and ``qsize``. They can be ``Size`` or ``None``, and
        ``QSize`` or ``None``, respectively.
    """

    count_size = 0
    count_qsize_min = 0
    count_qsize_max = 0

    for member in obj:
        if isinstance(member, BaseTypeDef):
            if member.size.size > count_size:
                count_size = member.size.size

            if member.qsize.min > count_qsize_min:
                count_qsize_min = member.qsize.min

            if member.qsize.max is not None and member.qsize.max > count_qsize_max:
                count_qsize_max = member.qsize.max

    size = Size(count_size) if count_size > 0 else None
    qsize = (
        None
        if count_qsize_min == 0
        else QSize(count_qsize_min, count_qsize_max or None)
    )
    return size, qsize
