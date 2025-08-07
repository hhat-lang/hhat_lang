from __future__ import annotations

from abc import abstractmethod
from enum import auto
from typing import Any, cast

from hhat_lang.core.code.new_ir import (
    BaseIR, BaseIRFlag, BaseIRInstr, RefTable,
)
from hhat_lang.core.code.abstract_new_ir import BaseIRBlock, BaseIRBlockFlag
from hhat_lang.core.data.core import (
    Symbol,
    CompositeSymbol,
    WorkingData,
    CompositeWorkingData,
    CoreLiteral,
    CompositeLiteral,
)
from hhat_lang.core.data.fn_def import BaseFnCheck
from hhat_lang.core.data.utils import VariableKind
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import HeapInvalidKeyError
from hhat_lang.core.memory.core import (
    MemoryManager,
)
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.core.types.builtin_types import builtins_types
from hhat_lang.core.types.builtin_conversion import compatible_types


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
        *args: IRBlock | IRInstr | WorkingData | CompositeWorkingData,
        name: IRFlag
    ):
        if (
            all(isinstance(k, IRBlock | IRInstr | WorkingData | CompositeWorkingData) for k in args)
            and isinstance(name, IRFlag)
        ):
            self._name = name
            self.args = args

        else:
            raise ValueError(
                f"IR instr {self.__class__.__name__} must received name as {type(name)},"
                f" args as {[type(k) for k in args]}. Check for correct types."
            )

    @abstractmethod
    def resolve(self, mem: MemoryManager, **kwargs: Any) -> Any:
        """
        To resolve pending type imports to ``IRTypes`` and function imports to ``IRFns``,
        type checks on built-in types or custom types at ``IRTypes`` or var checks in the
        ``Heap`` memory, and so on.
        """

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(str(k) for k in self.args)})"


class CastInstr(IRInstr):
    def __init__(
        self,
        data: WorkingData | CompositeWorkingData | IRInstr,
        to_type: WorkingData | CompositeWorkingData | ModifierBlock
    ):
        if (
            isinstance(data, WorkingData | CompositeWorkingData | IRInstr)
            and isinstance(to_type, WorkingData | CompositeWorkingData | ModifierBlock)
        ):
            super().__init__(data, to_type, name=IRFlag.CAST)

        else:
            raise ValueError(
                f"cast operation cannot contain {data} ({type(data)}) "
                f"and {to_type} ({type(to_type)})"
            )

    def resolve(self, mem: MemoryManager, **kwargs: Any) -> None:
        raise NotImplementedError()


class CallInstr(IRInstr):
    def __init__(
        self,
        name: Symbol | CompositeSymbol | ModifierBlock,
        *,
        args: ArgsBlock | ArgsValuesBlock | WorkingData | CompositeWorkingData | None = None,
        option: OptionBlock | None = None,
        body: BodyBlock | None = None,
    ):
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

    def resolve(self, mem: MemoryManager, **_: Any) -> None:
        caller: Symbol | CompositeSymbol | ModifierBlock = cast(Symbol | CompositeSymbol | ModifierBlock, self.args[0])
        args: tuple = self.args[1:]
        num_args: int = len(args)
        mem.scope.stack[mem.cur_scope].push(args)

        _handle_call_args(mem)

        _handle_call_instr(
            caller=caller,
            number_args=num_args,
            mem=mem,
            flag=self.name
        )


class DeclareInstr(IRInstr):
    def __init__(self, var: Symbol | ModifierBlock, var_type: Symbol | CompositeSymbol | ModifierBlock):
        if (
            isinstance(var, Symbol | ModifierBlock)
            and isinstance(var_type, Symbol | CompositeSymbol | ModifierBlock)
        ):
            super().__init__(var, var_type, name=IRFlag.DECLARE)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)} and var type must be symbol"
                f" or composite symbol, got {type(var_type)}"
            )

    def resolve(self, mem: MemoryManager, **_: Any) -> None:
        var: Symbol | ModifierBlock = cast(Symbol | ModifierBlock, self.args[0])
        _declare_variable(var=var, mem=mem)


class AssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        value: WorkingData | CompositeWorkingData | IRBlock
    ):
        if (
            isinstance(var, Symbol | ModifierBlock)
            and isinstance(value, WorkingData | CompositeWorkingData | IRBlock)
        ):
            super().__init__(var, value, name=IRFlag.ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    def resolve(self, mem: MemoryManager, **_: Any) -> None:
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

        _assign_variable(variable=variable, mem=mem)


class DeclareAssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        var_type: Symbol | CompositeSymbol | ModifierBlock,
        value: WorkingData | CompositeWorkingData | IRInstr | IRBlock,
    ):
        if (
            isinstance(var, Symbol | ModifierBlock)
            and isinstance(var_type, Symbol | CompositeSymbol | ModifierBlock)
            and isinstance(value, WorkingData | CompositeWorkingData | IRInstr | IRBlock)
        ):
            super().__init__(var, var_type, value, name=IRFlag.DECLARE_ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)}, "
                f"var type must be symbol or composite symbol, got {type(var_type)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    def resolve(self, mem: MemoryManager, **_: Any) -> None:
        var: Symbol = cast(Symbol, self.args[0])
        _declare_variable(var=var, mem=mem)
        variable: BaseDataContainer = mem.scope.heap[mem.cur_scope].get(var)
        mem.scope.stack[mem.cur_scope].push(self.args[2])
        _assign_variable(variable=variable, mem=mem)


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


class IRBlock(BaseIRBlock):
    """
    IR blocks
    """

    _name: IRBlockFlag

    def __len__(self) -> int:
        return len(self.args)

    def __getitem__(self, item: Any) -> Any:
        return self.args[item]


class BodyBlock(IRBlock):
    _name: IRBlockFlag.BODY

    def __init__(self, *args: IRBlock | IRInstr):
        if all(isinstance(k, IRBlock | IRInstr) for k in args):
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
    _name: IRBlockFlag.ARGS
    args: tuple[WorkingData | CompositeWorkingData | IRBlock | IRInstr, ...] | tuple

    def __init__(self, *args: WorkingData | CompositeWorkingData | IRBlock | IRInstr):
        if all(isinstance(k, WorkingData | CompositeWorkingData | IRBlock | IRInstr) for k in args):
            self.args = args

        else:
            raise ValueError(
                f"args must be block or instruction, but got {tuple(type(k) for k in args)}"
            )

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


class ArgsValuesBlock(IRBlock):
    _name: IRBlockFlag.ARGS_VALUES
    args: tuple[
              Symbol | CompositeSymbol | ModifierBlock, WorkingData | CompositeWorkingData | IRBlock | IRInstr
          ] | tuple

    def __init__(
        self,
        *args: tuple[Symbol | CompositeSymbol | ModifierBlock, WorkingData | CompositeWorkingData | IRBlock | IRInstr]
    ):
        if all(
            isinstance(k[0], Symbol | CompositeSymbol | ModifierBlock)
            and isinstance(k[1], WorkingData | CompositeWorkingData | IRBlock | IRInstr)
            for k in args
        ):
            self.args = args[0]

        else:
            raise ValueError(
                f"args must be symbols and values must be symbol, composite symbols,"
                f" block or instruction, but got {tuple(type(k) for k in args)}"
            )

    @property
    def arg(self) -> Symbol | CompositeSymbol | ModifierBlock:
        return self.args[0]

    @property
    def value(self) -> WorkingData | CompositeWorkingData | IRBlock | IRInstr:
        return self.args[1]

    def __repr__(self) -> str:
        return f"ARG-VALUE#[{self.arg}:{self.value}]"


class OptionBlock(IRBlock):
    _name: IRBlockFlag.OPTION
    args: tuple[
              tuple[WorkingData | CompositeWorkingData | IRBlock | IRInstr, ...],
              IRBlock | IRInstr
          ] | tuple

    def __init__(
        self,
        option: WorkingData | CompositeWorkingData | IRBlock | IRInstr,
        block: IRBlock | IRInstr,
    ):
        if (
            isinstance(option, WorkingData | CompositeWorkingData | IRBlock | IRInstr)
            and isinstance(block, WorkingData | CompositeWorkingData | IRBlock | IRInstr)
        ):
            self.args = (option, block)

        else:
            raise ValueError(f"option ({type(option)}) or block ({type(block)}) is of wrong type.")

    @property
    def option(self) -> WorkingData | CompositeWorkingData | IRBlock | IRInstr:
        return self.args[0]

    @property
    def block(self) -> WorkingData | CompositeWorkingData | IRBlock | IRInstr:
        return self.args[1]

    def __repr__(self) -> str:
        return f"OPTION#[{self.args[0]}:{self.args[1]}]"


class ReturnBlock(IRBlock):
    _name: IRBlockFlag.RETURN
    args: tuple[WorkingData | CompositeWorkingData | IRBlock | IRInstr, ...]

    def __init__(self, *args: WorkingData | CompositeWorkingData | IRBlock | IRInstr):
        if all(
            isinstance(k, WorkingData | CompositeWorkingData | IRBlock | IRInstr) for k in args
        ):
            self.args = args

        else:
            raise ValueError("return block got wrong object types")

    def __repr__(self) -> str:
        return f"RETURN#[{' '.join(str(k) for k in self.args)}]"


class ModifierBlock(IRBlock):
    _name: IRBlockFlag.MODIFIER
    args: tuple[Symbol | CompositeSymbol | IRInstr, ModifierArgsBlock]

    def __init__(self, obj: Symbol | CompositeSymbol | IRInstr, args: ModifierArgsBlock):
        if (
            isinstance(obj, Symbol | CompositeSymbol | IRInstr)
            and isinstance(args, ModifierArgsBlock)
        ):
            self.args = (obj, args)

        else:
            raise ValueError(f"modifier block cannot have types {type(obj)} and {type(args)}")

    @property
    def obj(self) -> Symbol | CompositeSymbol | IRInstr:
        return self.args[0]

    @property
    def mods(self) -> ModifierArgsBlock:
        return self.args[1]

    def __repr__(self) -> str:
        return f"{self.obj}<{self.mods}>"


class ModifierArgsBlock(IRBlock):
    _name: IRBlockFlag.MODIFIER_ARGS
    args: tuple[ArgsValuesBlock, ...] | tuple

    def __init__(
        self,
        args: tuple[Symbol | CompositeSymbol, ...] | ArgsValuesBlock | ArgsBlock
    ):
        if (
            isinstance(args, ArgsValuesBlock | ArgsBlock)
            or all(isinstance(k, Symbol | CompositeSymbol) for k in args)
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

class IR(BaseIR):
    """Hold all the IR content: IR blocks, IR types and IR functions"""

    _main: BodyBlock | None

    def __init__(
        self,
        *,
        ref_table: RefTable,
        symbol_table: SymbolTable | None = None,
        main: BodyBlock | None = None,
    ):
        if (
            isinstance(main, BodyBlock)
            or main is None
            and isinstance(symbol_table, SymbolTable)
            or symbol_table is None
            and isinstance(ref_table, RefTable)
        ):
            if main is None and symbol_table or main and symbol_table is None:
                self._main = main
                self._symbol_table = symbol_table
                self._ref_table = ref_table

            else:
                raise ValueError("cannot have main IR block and symbol table in the same IR")

    def __repr__(self) -> str:
        if self.main is not None:
            main = ""
            for k in self.main:
                main += f"       {k}\n"

        else:
            main = ""

        if self.symbol_table is not None:
            st = ""
            for k in self.symbol_table.type:
                st += f"       {k}\n"

            for k in self.symbol_table.fn:
                st += f"       {k}\n"

        else:
            st = ""

        return f"\n[ir/start]\n{st}  main:\n{main}\n[ir/end]\n"


##################
# MISC FUNCTIONS #
##################

def _declare_variable(
    var: Symbol | ModifierBlock,
    mem: MemoryManager
) -> None:
    """
    Convenient function for resolving variable declaration during the execution execution
    and store it on the heap memory from the current scope.

    Args:
        var: the actual variable; must be a ``Symbol`` or ``ModifierBlock`` object
        mem: ``MemoryManager`` object
    """

    # we just need the variable for now
    var = var.args[0] if isinstance(var, ModifierBlock) else var
    # TODO: make use of the modifier property through a new code logic later

    if var in mem.scope.heap[mem.cur_scope]:
        raise ValueError(f"{var} already in heap; cannot re-declare variable")

    vt: str | tuple[str, ...] = var.type
    type_symbol: Symbol | CompositeSymbol

    match vt:
        case str():
            type_symbol = Symbol(vt)

        case tuple():
            type_symbol = CompositeSymbol(vt)

        case _:
            raise ValueError(f"var type {vt} is not valid ({type(vt)})")

    var_type = mem.symbol.type.get(type_symbol, None) or builtins_types.get(type_symbol, None)

    match var_type:
        case None:
            raise ValueError(
                f"var type {var_type} not found on available custom and built-in types"
            )

        case BaseTypeDataStructure():
            var_container = var_type(
                var_name=var,
                # TODO: use the modifier to define variable flag and define a default
                flag=VariableKind.MUTABLE
            )

            match var_container:
                case BaseDataContainer():
                    mem.scope.heap[mem.cur_scope].set(key=var, value=var_container)

                case _:
                    raise ValueError(f"{var_container}")

        case _:
            raise NotImplementedError(
                f"{var_type} ({type(var_type)}) not implemented yet for variable declaration"
            )


def _get_assign_datatype(
    var_type: Symbol | CompositeSymbol,
    value: WorkingData | CompositeWorkingData | IRInstr | IRBlock,
    mem: MemoryManager,
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
        value: data name as ``WorkingData``, ``CompositeWorkingData``, ``IRInstr`` or
            ``IRBlock`` object to be assigned to the variable
        mem: ``MemoryManager`` object

    Returns:
        The data name with adjusted type (if possible) or raise an error, in case data
         is not compatible
    """

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
            data_type = Symbol(value.type)
            data_type = compatible_types.get(data_type) or data_type

            if var_type == data_type:
                dt_ds = builtins_types.get(data_type)

                if dt_ds:
                    mem.symbol.type.add(data_type, dt_ds)

                else:
                    raise ValueError(f"invalid type {data_type}")

                return CoreLiteral(value.value, data_type.value)

        case CompositeLiteral():
            raise NotImplementedError(
                "composite literal on variable assignment not implemente yet"
            )

        case IRInstr():
            new_args = ()

            for k in value:
                new_args += _get_assign_datatype(
                    var_type=var_type,
                    value=k,
                    mem=mem,
                ),

            new_instr: IRInstr = value.__class__(*new_args, name=value.name)
            new_instr.resolve(mem)

            return mem.scope.stack[mem.cur_scope].pop()

        case BodyBlock() | ArgsBlock() | ArgsValuesBlock() | OptionBlock():
            new_blocks = ()

            for k in value:
                new_blocks += _get_assign_datatype(
                    var_type=var_type,
                    value=k,
                    mem=mem
                ),

            new_instr: IRInstr = value.__class__(*new_blocks)
            new_instr.resolve(mem=mem)

            return mem.scope.stack[mem.cur_scope].pop()

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
    **arg_values: Any
) -> None:
    """
    Convenient function to assign a value to a variable. It calls checks for any
    data incompatibility and resolvers for any instructions or blocks to be yet
    evaluated.

    Args:
        variable: the variable container object
        stack_table: stack memory object from the current scope
        heap_table: heap memory object from the current scope
        types_table: ``IRTypes`` types table object
        **arg_values: Any extra argument used
    """

    args: WorkingData | CompositeWorkingData | IRInstr | IRBlock = mem.scope.stack[mem.cur_scope].pop()
    new_args: tuple = _get_assign_datatype(var_type=variable.type, value=args, mem=mem),

    if len(new_args) > 0 and len(arg_values) == 0:
        variable.assign(*new_args)

    elif len(new_args) == 0 and len(arg_values) > 0:
        variable.assign(**arg_values)

    else:
        raise NotImplementedError(
            f"should not have arguments and argument-value together when "
            f"assigning variable {variable}"
        )


def _handle_call_args(mem: MemoryManager) -> None:
    """
    Convenient function to resolve call arguments.

    Args:
        mem: ``MemoryManager`` object
    """

    args: tuple | IRBlock | IRInstr | WorkingData | CompositeWorkingData = mem.scope.stack[mem.cur_scope].pop()

    match args:
        case tuple() | IRBlock():
            for k in args:
                mem.scope.stack[mem.cur_scope].push(k)
                _handle_call_args(mem)

        case IRInstr():
            args.resolve(mem)

        case WorkingData() | CompositeWorkingData():
            mem.scope.stack[mem.cur_scope].push(args)


def _handle_call_instr(
    caller: Symbol | CompositeSymbol,
    number_args: int,
    mem: MemoryManager,
    flag: IRFlag
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
            args_types = ()
            args = ()

            for _ in range(number_args):
                res = mem.scope.stack[mem.cur_scope].pop()
                args += res,

                if isinstance(res, CoreLiteral):
                    args_types += res.type,

                elif isinstance(res, Symbol):
                    args_types += res

            fn_entry = BaseFnCheck(
                fn_name=caller,
                args_types=args_types,
            )
            fn_block: IRBlock = cast(IRBlock, mem.symbol.fn.get(fn_entry, None))

            if fn_block is None:
                raise ValueError(f"function {caller} with arg type signature {args_types} not found")

            # FIXME: depth_counter value needs to come from the execution global depth counter
            fn_scope = mem.new_scope(fn_block, depth_counter=1)
            _resolve_fn_block(fn_block, mem)
            mem.free_last_scope(to_return=True)

        case IRFlag.CALL_WITH_BODY:
            pass

        case IRFlag.CALL_WITH_OPTION:
            pass
    pass


def _resolve_fn_block(
    data: IRBlock | IRInstr,
    mem: MemoryManager
) -> None:
    """
    Convenient function to resolve function blocks. Whenever it's called from outside,
    a new scope from ``MemoryManager`` must be created and freed after it finishes
    execution and return to the outside scope.

    Args:
        data: IR block or IR instruction object
        mem: ``MemoryManager`` object
    """

    match data:
        case IRBlock():
            for k in data:
                _resolve_fn_block(k, mem)

        case IRInstr():
            data.resolve(mem)
