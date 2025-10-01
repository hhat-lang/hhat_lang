from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from enum import auto
from pathlib import Path
from typing import Any, cast, Callable

from hhat_lang.core.code.abstract import BaseIR, BaseIRModule, IRHash, RefTable
from hhat_lang.core.code.base import (
    BaseFnCheck,
    BaseIRBlock,
    BaseIRBlockFlag,
    BaseIRFlag,
    BaseIRInstr,
)
from hhat_lang.core.code.new_ir import (
    IRGraph,
    IRNode,
    get_type,
)
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeSymbol,
    CompositeWorkingData,
    CoreLiteral,
    Symbol,
    WorkingData,
)
from hhat_lang.core.data.utils import VariableKind
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import HeapInvalidKeyError
from hhat_lang.core.memory.core import (
    MemoryManager,
)
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.core.types.builtin_conversion import compatible_types
from hhat_lang.core.types.builtin_types import builtins_types
from hhat_lang.dialects.heather.code.builtins.fns import BUILTIN_FNS_DICT


###########################
# IR INSTRUCTIONS CLASSES #
###########################

class IRFlag(BaseIRFlag):
    """
    Used to identify the ``IRBaseInstr`` child class purpose. Ex: a ``CallInstr``
    class is defined with its name as ``IRFlag.CALL``.
    """

    NULL = auto()
    CALL = auto()
    CAST = auto()
    ASSIGN = auto()
    DECLARE = auto()
    DECLARE_ASSIGN = auto()
    ARGS = auto()
    ARG_VALUE = auto()
    OPTION = auto()
    COND = auto()
    MATCH = auto()
    CALL_WITH_BODY = auto()
    CALL_WITH_OPTION = auto()
    RETURN = auto()


class BuiltinInstr(BaseIRInstr):
    def __init__(self, *args: Any, name: Symbol, flag: IRFlag):
        self.args = (name, args)
        self._name = flag
        super().__init__()

    @property
    def builtin_name(self) -> Symbol:
        return cast(Symbol, self.args[0])

    @property
    def builtin_args(self) -> tuple[Any, ...] | tuple:
        return self.args[1:]

    def resolve(
        self,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        **kwargs: Any
    ) -> Any:
        """

        Args:
            mem: ``MemoryManager`` instance
            node: ``IRNode`` instance
            ir_graph: ``IRGraph`` instance
            **kwargs: extra arguments for the function to work

        Returns:
            Whatever the built-in function should return
        """

        fns_dict: dict[tuple, Callable] = BUILTIN_FNS_DICT[self.builtin_name.value]
        args_types = _handle_call_args(*self.builtin_args,  mem=mem, node=node, ir_graph=ir_graph)
        builtin_fn: Callable = fns_dict[args_types]
        # TODO: call builtin_fn() directly or _handle_call_instr() ?
        # builtin_fn(*self.builtin_args)

    def __repr__(self) -> str:
        return f"{self.name}({' '.join(str(k) for k in self.args)})"


class IRInstr(BaseIRInstr):
    """
    Base class for IR instructions. Custom IR instructions names must adhere to
    IRFlag enum attributes. For example::


        class DeclareInstr(IRInstr):
            def __init__(self, ...):
                ...
                super().__init__(..., name=IRFlag.DECLARE)
    """

    _name: IRFlag
    args: tuple[IRBlock | WorkingData | CompositeWorkingData, ...] | tuple

    def __init__(
        self,
        *args: IRBlock | BaseIRInstr | WorkingData | CompositeWorkingData,
        name: IRFlag,
    ):
        if all(
            isinstance(k, IRBlock | BaseIRInstr | WorkingData | CompositeWorkingData)
            for k in args
        ) and isinstance(name, IRFlag):
            self._name = name
            self.args = args
            super().__init__()

        else:
            raise ValueError(
                f"IR instr {self.__class__.__name__} must received name as {type(name)},"
                f" args as {[type(k) for k in args]}. Check for correct types."
            )

    @abstractmethod
    def resolve(
        self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **kwargs: Any
    ) -> Any:
        """
        To resolve instructions during code execution.
        """

        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(str(k) for k in self.args)})"


class CastInstr(IRInstr):
    def __init__(
        self,
        data: WorkingData | CompositeWorkingData | BaseIRInstr,
        to_type: WorkingData | CompositeWorkingData | ModifierBlock,
    ):
        if isinstance(
            data, WorkingData | CompositeWorkingData | BaseIRInstr
        ) and isinstance(to_type, WorkingData | CompositeWorkingData | ModifierBlock):
            super().__init__(data, to_type, name=IRFlag.CAST)

        else:
            raise ValueError(
                f"cast operation cannot contain {data} ({type(data)}) "
                f"and {to_type} ({type(to_type)})"
            )

    def resolve(self, mem: MemoryManager, ir_graph: IRGraph, **kwargs: Any) -> None:
        raise NotImplementedError()


class CallInstr(IRInstr):
    def __init__(
        self,
        name: Symbol | CompositeSymbol | ModifierBlock,
        *,
        args: (
            ArgsBlock | ArgsValuesBlock | WorkingData | CompositeWorkingData | None
        ) = None,
        option: OptionBlock | None = None,
        body: BodyBlock | None = None,
    ):
        instr_args: tuple[IRBlock | BaseIRInstr | WorkingData] | tuple

        if option is None and body is None:
            instr_args = (args,)
            flag = IRFlag.CALL

        elif option is not None and body is None:
            instr_args = (option,)
            flag = IRFlag.CALL_WITH_OPTION

        elif option is None and body is not None:
            instr_args = (args, body)
            flag = IRFlag.CALL_WITH_BODY

        else:
            raise ValueError(
                f"cannot contain option ({type(option)}) and body ({type(body)}) "
                f"in the same instruction."
            )

        super().__init__(name, *instr_args, name=flag)

    def resolve(
        self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any
    ) -> None:
        caller: Symbol | CompositeSymbol = (
            self.args[0]  # type: ignore [assignment]
            if isinstance(self.args[0], Symbol | CompositeSymbol)
            else (
                self.args[0].name
                if isinstance(self.args[0], ModifierBlock)
                else sys.exit("call instr error")
            )
        )
        args: tuple = self.args[1:]
        num_args: int = len(args)
        resolved_args = _handle_call_args(*args, mem=mem, node=node, ir_graph=ir_graph)

        fn_header = BaseFnCheck(fn_name=caller, args_types=resolved_args)
        mem.stack.new(for_fn_use=True)
        mem.stack.set_fn_entry(*args, fn_header=fn_header)
        _handle_call_instr(
            caller=caller,
            number_args=num_args,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
            flag=self.name,
        )


class DeclareInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        var_type: Symbol | CompositeSymbol | ModifierBlock,
    ):
        if isinstance(var, Symbol | ModifierBlock) and isinstance(
            var_type, Symbol | CompositeSymbol | ModifierBlock
        ):
            super().__init__(var, var_type, name=IRFlag.DECLARE)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)} and var type must be symbol"
                f" or composite symbol, got {type(var_type)}"
            )

    def resolve(
        self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any
    ) -> None:
        var: Symbol | ModifierBlock = cast(Symbol | ModifierBlock, self.args[0])
        var_type_symbol: Symbol | CompositeSymbol = cast(
            Symbol | CompositeSymbol, self.args[1]
        )
        _declare_variable(var, var_type_symbol, mem, node.irhash, ir_graph)


class AssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        value: WorkingData | CompositeWorkingData | IRBlock,
    ):
        if isinstance(var, Symbol | ModifierBlock) and isinstance(
            value, WorkingData | CompositeWorkingData | IRBlock
        ):
            super().__init__(var, value, name=IRFlag.ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    def resolve(
        self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any
    ) -> None:
        var: Symbol = cast(Symbol, self.args[0])
        variable = mem.scope.heap[mem.cur_scope].get(var)
        mem.scope.stack[mem.cur_scope].push(self.args[1])

        # # resolve value to check and assign the correct type
        # new_args = _get_assign_datatype(
        #     var_type=variable.type,
        #     value=value,
        #     heap_table=heap_table,
        #     types_table=types_table
        # )
        # # set new arguments
        # self.args = (self.args[0], *new_args)

        _assign_variable(variable=variable, mem=mem, node=node, ir_graph=ir_graph)


class DeclareAssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        var_type: Symbol | CompositeSymbol | ModifierBlock,
        value: WorkingData | CompositeWorkingData | BaseIRInstr | IRBlock,
    ):
        if (
            isinstance(var, Symbol | ModifierBlock)
            and isinstance(var_type, Symbol | CompositeSymbol | ModifierBlock)
            and isinstance(
                value, WorkingData | CompositeWorkingData | BaseIRInstr | IRBlock
            )
        ):
            super().__init__(var, var_type, value, name=IRFlag.DECLARE_ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)}, "
                f"var type must be symbol or composite symbol, got {type(var_type)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    def resolve(
        self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any
    ) -> None:
        var: Symbol = cast(Symbol, self.args[0])
        var_type_symbol: Symbol | CompositeSymbol = cast(
            Symbol | CompositeSymbol, self.args[1]
        )
        _declare_variable(var, var_type_symbol, mem, node.irhash, ir_graph)
        variable: BaseDataContainer = cast(BaseDataContainer, mem.stack.get(var))
        mem.stack.push(variable)
        _assign_variable(variable=variable, mem=mem, node=node, ir_graph=ir_graph)


####################
# IR BLOCK CLASSES #
####################


class IRBlockFlag(BaseIRBlockFlag):
    """Define all valid IR block flags for IR blocks"""

    BODY = auto()
    ARGS = auto()
    ARGS_VALUES = auto()
    OPTION = auto()
    RETURN = auto()
    MODIFIER = auto()
    MODIFIER_ARGS = auto()


class IRBlock(BaseIRBlock, ABC):
    """
    IR blocks
    """

    _name: IRBlockFlag

    def __len__(self) -> int:
        return len(self.args)

    def __getitem__(self, item: Any) -> Any:
        return self.args[item]


class BodyBlock(IRBlock):
    _name = IRBlockFlag.BODY

    def __init__(self, *args: IRBlock | BaseIRInstr):
        if all(isinstance(k, IRBlock | BaseIRInstr) for k in args):
            if len(args) == 1 and isinstance(args[0], BodyBlock):
                self.args = args[0].args

            else:
                self.args = args

        else:
            raise ValueError(
                f"args must be block or instruction, but got {tuple(type(k) for k in args)}"
            )

    def __repr__(self) -> str:
        return "\n".join(str(k) for k in self.args)


class ArgsBlock(IRBlock):
    _name = IRBlockFlag.ARGS

    args: tuple[WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr, ...] | tuple

    def __init__(self, *args: WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr):
        if all(
            isinstance(k, WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr)
            for k in args
        ):
            self.args = args

        else:
            raise ValueError(
                f"args must be block or instruction, but got {tuple(type(k) for k in args)}"
            )

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


class ArgsValuesBlock(IRBlock):
    _name = IRBlockFlag.ARGS_VALUES

    args: (
        tuple[
            Symbol,
            ...,
        ]
        | tuple
    )
    values: tuple[WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr, ...] | tuple

    def __init__(
        self,
        *args: tuple[
            Symbol,
            WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr,
        ],
    ):
        self.args = ()
        self.values = ()

        for k in args:
            if isinstance(k[0], Symbol):
                self.args += (k[0],)
            else:
                raise ValueError(
                    "args values block's args must be symbol or modifier block "
                )

            if isinstance(k[1], WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr):
                self.values += (k[1],)
            else:
                raise ValueError(
                    "args values block's values must be symbol, literal, ir block or ir instr"
                )

    def __repr__(self) -> str:
        return f"ARG-VALUE#[{' '.join(f'{a}:{v}' for a, v in zip(self.args, self.values))}]"


class OptionBlock(IRBlock):
    _name = IRBlockFlag.OPTION

    args: (  # type: ignore [assignment]
        tuple[
            tuple[WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr, ...],
            IRBlock | BaseIRInstr,
        ]
        | tuple
    )

    def __init__(
        self,
        option: WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr,
        block: IRBlock | BaseIRInstr,
    ):
        if isinstance(
            option, WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr
        ) and isinstance(block, WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr):
            self.args = (option, block)

        else:
            raise ValueError(
                f"option ({type(option)}) or block ({type(block)}) is of wrong type."
            )

    @property
    def option(self) -> WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr:
        return self.args[0]

    @property
    def block(self) -> WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr:
        return self.args[1]

    def __repr__(self) -> str:
        return f"OPTION#[{self.args[0]}:{self.args[1]}]"


class ReturnBlock(IRBlock):
    _name = IRBlockFlag.RETURN

    args: tuple[WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr, ...]

    def __init__(self, *args: WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr):
        if all(
            isinstance(k, WorkingData | CompositeWorkingData | IRBlock | BaseIRInstr)
            for k in args
        ):
            self.args = args

        else:
            raise ValueError("return block got wrong object types")

    def __repr__(self) -> str:
        return f"RETURN#[{' '.join(str(k) for k in self.args)}]"


class ModifierBlock(IRBlock):
    _name = IRBlockFlag.MODIFIER

    args: tuple[Symbol | CompositeSymbol | BaseIRInstr, ModifierArgsBlock]

    def __init__(
        self, obj: Symbol | CompositeSymbol | BaseIRInstr, args: ModifierArgsBlock
    ):
        if isinstance(obj, Symbol | CompositeSymbol | BaseIRInstr) and isinstance(
            args, ModifierArgsBlock
        ):
            self.args = (obj, args)

        else:
            raise ValueError(
                f"modifier block cannot have types {type(obj)} and {type(args)}"
            )

    @property
    def obj(self) -> Symbol | CompositeSymbol | BaseIRInstr:
        return self.args[0]

    @property
    def mods(self) -> ModifierArgsBlock:
        return self.args[1]

    def __repr__(self) -> str:
        return f"{self.obj}<{self.mods}>"


class ModifierArgsBlock(IRBlock):
    _name = IRBlockFlag.MODIFIER_ARGS

    args: tuple[Symbol | CompositeSymbol, ...] | ArgsValuesBlock | ArgsBlock  # type: ignore [assignment]

    def __init__(
        self, args: tuple[Symbol | CompositeSymbol, ...] | ArgsValuesBlock | ArgsBlock
    ):
        if isinstance(args, ArgsValuesBlock | ArgsBlock) or all(
            isinstance(k, Symbol | CompositeSymbol) for k in args
        ):
            self.args = args

        else:
            raise ValueError(
                f"modifier args must be made of ArgsValuesBlock elements, "
                f"not {[type(k) for k in args]}"
            )

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


##############
# IR CLASSES #
##############


class IRModule(BaseIRModule):
    def __init__(
        self,
        path: Path,
        symboltable: SymbolTable,
        main: BodyBlock | None = None,
    ):
        self._path = path
        self._symbol_table = symboltable
        self._main = main or BodyBlock()

    def __str__(self) -> str:
        st = ""
        if self.symbol_table.type:
            st += f"{self.symbol_table.type}"

        if self.symbol_table.fn:
            st += f"{self.symbol_table.fn}"

        if st:
            st = f"\n  - symbol table:{st}"

        main = ""
        if self.main:
            main += "\n  - main:\n      "
            main += "\n      ".join(str(k) for k in self.main)
            main += "\n"

        return f"{IRHash(self._path)}{st}{main}"


class IR(BaseIR):
    """Hold all the IR content: IR blocks, IR types and IR functions"""

    def __init__(
        self,
        *,
        ref_table: RefTable,
        ir_module: IRModule,
    ):
        if isinstance(ir_module, IRModule) and isinstance(ref_table, RefTable):
            self._module = ir_module
            self._ref_table = ref_table

        else:
            raise ValueError(
                "cannot have main IR block and symbol table in the same IR"
            )

    def __repr__(self) -> str:
        rf = ""

        if self.ref_table.types:
            rf += "\n".join(f"    {t}:{t_def}" for t, t_def in self.ref_table.types)

        if self.ref_table.fns:
            rf += "\n".join(f"    {f}:{f_def}" for f, f_def in self.ref_table.fns)

        if rf:
            rf = f"\n  ref table:\n{rf}\n"

        module = f"\n  module:{self.module}"

        return f"\n=IR:start={rf}{module}=IR:end=\n"


##################
# MISC FUNCTIONS #
##################


def _declare_variable(
    var: Symbol | CompositeSymbol | ModifierBlock,
    var_type_symbol: Symbol | CompositeSymbol,
    mem: MemoryManager,
    node_hash: IRHash,
    ir_graph: IRGraph,
) -> None:
    """
    Convenient function for resolving variable declaration during the execution execution
    and store it on the memory for further use.

    Args:
        var: the actual variable; must be a ``Symbol`` or ``ModifierBlock`` object
        var_type_symbol:
        mem: ``MemoryManager`` object
        node_hash:
        ir_graph:
    """

    # we just need the variable for now
    var_symbol = cast(
        Symbol | CompositeSymbol, var.args[0] if isinstance(var, ModifierBlock) else var
    )
    # TODO: make use of the modifier property through a new code logic later

    if var_symbol in mem.stack:
        raise ValueError(
            f"{var_symbol} already in scope memory; cannot re-declare variable"
        )

    var_type = get_type(
        node_key=node_hash, importing=var_type_symbol, ir_graph=ir_graph
    )

    match var_type:
        case None:
            raise ValueError(
                f"var type {var_type} not found on available custom and built-in types"
            )

        case BaseTypeDataStructure():
            var_container = var_type(
                var_name=var_symbol,
                # TODO: use the modifier to define variable flag and define a default as well
                flag=VariableKind.MUTABLE,
            )

            match var_container:
                case BaseDataContainer():
                    mem.stack.push(var_container)

                case _:
                    raise ValueError(f"{var_container}")

        case _:
            raise NotImplementedError(
                f"{var_type} ({type(var_type)}) not implemented yet for variable declaration"
            )


def _get_assign_datatype(
    var_type: Symbol | CompositeSymbol,
    value: WorkingData | CompositeWorkingData | BaseIRInstr | IRBlock,
    mem: MemoryManager,
    node: IRNode,
    ir_graph: IRGraph,
) -> Symbol | CoreLiteral | CoreLiteral | CompositeLiteral | BaseDataContainer:
    """
    Convenient function to: (1) check whether the data being assigned to the variable has
    the correct type, and to (2) resolve any instruction and block.

    For instance, ``int`` data type can be converted to any of the valid integer types,
    such as ``u64``, ``i64``, so on. However, if the data provided is a ``float`` and the
    variable is an integer (e.g. ``u64``), it cannot be converted implicitly, so an error
    will be raised. 'Convertible' data types should be done so explicitly on code,
    with ``*`` (cast) operation, ex::

        var1:u32 = 4.0*u32
        var2:f32 = 255*f32

    Data should be prepared to be inserted into the variable container, so any caller or
    casting should be resolved here.

    Args:
        var_type: ``CompositeSymbol`` (or ``Symbol``) object of the variable type
        value: data name as ``WorkingData``, ``CompositeWorkingData``, ``BaseIRInstr`` or
            ``IRBlock`` object to be assigned to the variable
        mem: ``MemoryManager`` object
        node:
        ir_graph:

    Returns:
        The data name with adjusted type (if possible) or raise an error, in case data
         is not compatible
    """

    new_instr: BaseIRInstr

    match value:
        case Symbol():
            res_var = mem.scope.heap[mem.cur_scope].get(value)

            match res_var:
                case HeapInvalidKeyError():
                    raise ValueError(f"variable {value} is not declared yet")

                case _:
                    if res_var.type == var_type:
                        return value

        case CompositeSymbol():
            raise NotImplementedError(
                "composite symbol on variable assignment not implemented yet"
            )

        case CoreLiteral():
            data_type = (
                Symbol(value.type)
                if isinstance(value.type, str)
                else CompositeSymbol(value.type)
            )
            data_type_tuple = compatible_types.get(data_type, None) or (data_type,)  # type: ignore [arg-type]

            if var_type in data_type_tuple:
                dt_ds = builtins_types.get(data_type)  # type: ignore [arg-type]

                if dt_ds:
                    mem.symbol.type.add(data_type, dt_ds)

                else:
                    raise ValueError(f"invalid type {data_type}")

                return CoreLiteral(value.value, data_type.value)

        case CompositeLiteral():
            raise NotImplementedError(
                "composite literal on variable assignment not implemente yet"
            )

        case BaseIRInstr():
            new_args: (
                tuple[WorkingData | CompositeWorkingData | BaseDataContainer] | tuple
            ) = ()

            for k in value:
                new_args += (
                    _get_assign_datatype(
                        var_type=var_type,
                        value=k,
                        mem=mem,
                        node=node,
                        ir_graph=ir_graph,
                    ),
                )

            new_instr = value.__class__(*new_args, name=value.name)
            new_instr.resolve(mem, node, ir_graph)

            return mem.scope.stack[mem.cur_scope].pop()

        case BodyBlock() | ArgsBlock() | ArgsValuesBlock():
            new_blocks: (
                tuple[WorkingData | CompositeWorkingData | BaseDataContainer] | tuple
            ) = ()

            for k in value:
                new_blocks += (
                    _get_assign_datatype(
                        var_type=var_type,
                        value=k,
                        mem=mem,
                        node=node,
                        ir_graph=ir_graph,
                    ),
                )

            new_instr = cast(IRInstr, value.__class__(*new_blocks))
            new_instr.resolve(mem=mem, node=node, ir_graph=ir_graph)

            return mem.scope.stack[mem.cur_scope].pop()

        case OptionBlock():
            # FIXME: implement option block
            raise NotImplementedError()

        case _:
            raise NotImplementedError(
                f"{value} ({type(value)}) on variable assignment with undefined implementation"
            )

    raise ValueError(
        f"data {value} to be assigned is not compatible with target type {var_type}"
    )


def _assign_variable(
    *,
    variable: BaseDataContainer,
    mem: MemoryManager,
    node: IRNode,
    ir_graph: IRGraph,
    **arg_values: Any,
) -> None:
    """
    Convenient function to assign a value to a variable. It calls checks for any
    data incompatibility and resolvers for any instructions or blocks to be yet
    evaluated.

    Args:
        variable: the variable container object
        mem:
        node:
        ir_graph:
        **arg_values: Any extra argument used
    """

    args: WorkingData | CompositeWorkingData | BaseIRInstr | IRBlock = mem.scope.stack[
        mem.cur_scope
    ].pop()
    new_args: tuple = (
        _get_assign_datatype(
            var_type=variable.type,
            value=args,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
        ),
    )

    if len(new_args) > 0 and len(arg_values) == 0:
        variable.assign(*new_args)

    elif len(new_args) == 0 and len(arg_values) > 0:
        variable.assign(**arg_values)

    else:
        raise NotImplementedError(
            f"should not have arguments and argument-value together when "
            f"assigning variable {variable}"
        )


def _get_type_from_data(
    data: BaseDataContainer | CoreLiteral,
) -> Symbol | CompositeSymbol:
    if isinstance(data, CoreLiteral):
        return (
            Symbol(data.type)
            if isinstance(data.type, str)
            else CompositeSymbol(data.type)
        )

    if isinstance(data, BaseDataContainer):
        return data.type

    sys.exit(f"unknown arg value on call args resolution ({type(data)})")


def _handle_call_args(
    *args: IRBlock | BaseIRInstr | WorkingData | CompositeWorkingData,
    mem: MemoryManager,
    node: IRNode,
    ir_graph: IRGraph,
) -> tuple[CoreLiteral | BaseDataContainer, ...] | tuple:
    """
    Convenient function to resolve call arguments.

    Args:
        *args:
        mem: ``MemoryManager`` object
        node:
        ir_graph:
    """

    resolved_args: tuple[Symbol | CompositeSymbol, ...] | tuple = ()

    for arg in args:
        match arg:
            case tuple() | IRBlock():
                for k in arg:
                    resolved_args += _handle_call_args(
                        *k, mem=mem, node=node, ir_graph=ir_graph
                    )

            case BaseIRInstr():
                arg.resolve(mem, node, ir_graph)
                res_return = mem.stack.get_fn_return()
                resolved_args += (_get_type_from_data(res_return),)

            case Symbol() | CompositeSymbol():
                resolved_args += (_get_type_from_data(mem.stack.get(arg)),)

            case CoreLiteral():
                resolved_args += (arg,)

    return resolved_args


def _handle_call_instr(
    caller: Symbol | CompositeSymbol | ModifierBlock,
    number_args: int,
    mem: MemoryManager,
    node: IRNode,
    ir_graph: IRGraph,
    flag: IRFlag,
) -> None:
    """
    Convenient function to handle call instruction and evaluated it.

    Args:
        caller: the caller name
        number_args: number of arguments; needed to pop data out of the stack the
            correct amount of times
        mem: ``MemoryManager`` object
        flag: ``IRFlag`` value
    """

    match flag:
        case IRFlag.CALL:
            args_types: tuple[WorkingData] | tuple = ()
            args: tuple[BaseDataContainer] | tuple = ()

            for _ in range(number_args):
                res = mem.stack.pop()
                args += (res,)

                if isinstance(res, CoreLiteral):
                    args_types += (res.type,)

                elif isinstance(res, Symbol):
                    args_types += (res,)

            # TODO: implement modifier resolution before proceeding on function definition

            caller = caller[0] if isinstance(caller, ModifierBlock) else caller
            fn_entry = BaseFnCheck(
                fn_name=caller,
                args_types=args_types,
            )
            fn_block: IRBlock = cast(IRBlock, mem.symbol.fn.get(fn_entry, None))

            if fn_block is None:
                raise ValueError(
                    f"function {caller} with arg type signature {args_types} not found"
                )

            # FIXME: depth_counter value needs to come from the execution global depth counter
            fn_scope = mem.new_scope(fn_block, depth_counter=1)
            _resolve_fn_block(fn_block, mem, node, ir_graph)
            mem.free_last_scope(to_return=True)

        case IRFlag.CALL_WITH_BODY:
            pass

        case IRFlag.CALL_WITH_OPTION:
            pass
    pass


def _resolve_fn_block(
    data: IRBlock | BaseIRInstr, mem: MemoryManager, node: IRNode, ir_graph: IRGraph
) -> None:
    """
    Convenient function to resolve function blocks. Whenever it's called from outside,
    a new scope from ``MemoryManager`` must be created and freed after it finishes
    execution and return to the outside scope.

    Args:
        data: IR block or IR instruction object
        mem: ``MemoryManager`` object
        node:
        ir_graph:
    """

    match data:
        case IRBlock():
            for k in data:
                _resolve_fn_block(k, mem, node, ir_graph)

        case BaseIRInstr():
            data.resolve(mem=mem, node=node, ir_graph=ir_graph)

