from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, cast, Callable

from hhat_lang.core.code.abstract import BaseIR, BaseIRModule, IRHash, RefTable
from hhat_lang.core.code.base import (
    FnHeader,
    BaseIRInstr,
)
from hhat_lang.core.code.ir_block import (
    IRFlag,
    IRBlock,
    IRInstr,
)
from hhat_lang.core.code.ir_custom import (
    ArgsValuesBlock,
    BodyBlock,
    ReturnBlock,
    ModifierBlock,
    ArgsBlock,
    OptionBlock,
)
from hhat_lang.core.code.ir_graph import (
    IRGraph,
    IRNode,
)
from hhat_lang.core.code.tools import (
    get_type,
    get_fn,
)
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.data.core import (
    LiteralArray,
    CompositeSymbol,
    ObjArray,
    Literal,
    Symbol,
    SimpleObj,
)
from hhat_lang.core.data.fn_def import FnDef
from hhat_lang.core.data.utils import DataKind
from hhat_lang.core.error_handlers.errors import HeapInvalidKeyError
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.core.types.abstract_base import BaseTypeDef
from hhat_lang.core.types.builtin_conversion import compatible_types
from hhat_lang.core.types.builtin_types import builtins_types
from hhat_lang.dialects.heather.cast.base import CastQ2C, CastC2C, CastC2Q, CastQ2Q
from hhat_lang.core.data.var_def import DataDef

# from hhat_lang.dialects.heather.code.builtins.fns import BUILTIN_FN_DICT


###########################
# IR INSTRUCTIONS CLASSES #
###########################


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

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **kwargs: Any) -> Any:
    #     """
    #
    #     Args:
    #         mem: ``MemoryManager`` instance
    #         node: ``IRNode`` instance
    #         ir_graph: ``IRGraph`` instance
    #         **kwargs: extra arguments for the function to work
    #
    #     Returns:
    #         Whatever the built-in function should return
    #     """
    #
    #     fns_dict: dict[tuple, Callable] = BUILTIN_FN_DICT[self.builtin_name.value]
    #     args = _resolve_call_args(*self.builtin_args, mem=mem, node=node, ir_graph=ir_graph)
    #     args_types = _resolve_call_args_types(*args)
    #
    #     builtin_fn: Callable = fns_dict[args_types]
    #     # TODO: call builtin_fn() directly or through _handle_call_instr()?
    #     builtin_fn(*self.builtin_args)

    def __repr__(self) -> str:
        return f"{self.name}({' '.join(str(k) for k in self.args)})"


class CastInstr(IRInstr):
    def __init__(
        self,
        data: SimpleObj | ObjArray | ModifierBlock | BaseIRInstr,
        to_type: Symbol | CompositeSymbol | ModifierBlock,
    ):
        if isinstance(
            data, SimpleObj | ObjArray | ModifierBlock | BaseIRInstr
        ) and isinstance(to_type, Symbol | CompositeSymbol | ModifierBlock):
            super().__init__(data, to_type, name=IRFlag.CAST)

        else:
            raise ValueError(
                f"cast operation cannot contain {data} ({type(data)}) "
                f"and {to_type} ({type(to_type)})"
            )

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **kwargs: Any) -> None:
    #     _data = _resolve_expr_to_data(self.args[0], mem, node, ir_graph)
    #     _type = _resolve_type(self.args[1], mem, node, ir_graph)
    #     _resolve_cast(_data, to_type=_type, mem=mem, node=node, ir_graph=ir_graph)


class CallInstr(IRInstr):
    def __init__(
        self,
        name: Symbol | CompositeSymbol | ModifierBlock,
        *,
        args: ArgsBlock | ArgsValuesBlock | SimpleObj | ObjArray | None = None,
        option: OptionBlock | None = None,
        body: BodyBlock | None = None,
    ):
        instr_args: tuple[IRBlock | BaseIRInstr | SimpleObj] | tuple

        if args is not None and option is None and body is None:
            instr_args = (args,)
            flag = IRFlag.FN_CALL

        elif args is None and option is not None and body is None:
            instr_args = (option,)
            flag = IRFlag.OPTN_CALL

        elif args is not None and option is not None and body is None:
            instr_args = (args, option)
            flag = IRFlag.OPTBDN_CALL

        elif option is None and body is not None:
            instr_args = (args, body)
            flag = IRFlag.BDN_CALL

        else:
            raise ValueError(
                f"cannot contain option ({type(option)}) and body ({type(body)}) "
                f"in the same instruction."
            )

        super().__init__(name, *instr_args, name=flag)

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any) -> None:
    #     match self.name:
    #         case IRFlag.BUILTIN_FN_CALL:
    #             args, fn_header = self._set_fn_call(ir_graph, mem, node)
    #             fn_def = get_fn(node_key=node.irhash, importing=fn_header, ir_graph=ir_graph)
    #
    #             # set new stack for function context; it's freed when exiting the context
    #             with mem.new_fn_stack(*args, fn_header=fn_header):
    #                 _resolve_builtin_fn(fn_def=fn_def, mem=mem, node=node, ir_graph=ir_graph)
    #
    #         case IRFlag.FN_CALL:
    #             args, fn_header = self._set_fn_call(ir_graph, mem, node)
    #             mem.stack.new(for_fn_use=True)
    #             mem.stack.set_fn_entry(*args, fn_header=fn_header)
    #             _handle_call_instr(
    #                 fn_header=fn_header,
    #                 mem=mem,
    #                 node=node,
    #                 ir_graph=ir_graph,
    #                 flag=self.name,
    #             )
    #             mem.stack.free()
    #
    #         # TODO: implement case for IRFlag.OPTN_CALL, IRFlag.BDN_CALL, IRFlag.OPTBDN_CALL
    #
    #         # case IRFlag.OPTN_CALL:
    #         #     pass
    #         #
    #         # case IRFlag.BDN_CALL:
    #         #     pass
    #         #
    #         # case IRFlag.OPTBDN_CALL:
    #         #     pass
    #
    #         case _:
    #             raise NotImplementedError(
    #                 f"resolve method from CallInstr for {self.name} not implemented"
    #             )
    #
    # def _set_fn_call(
    #     self, ir_graph: IRGraph, mem: MemoryManager, node: IRNode
    # ) -> tuple[tuple, BaseFnCheck]:
    #     caller: Symbol | CompositeSymbol | ModifierBlock = (
    #         cast(Symbol | CompositeSymbol, self.args[0])  # type: ignore [assignment]
    #         if isinstance(self.args[0], Symbol | CompositeSymbol)
    #         else (
    #             cast(ModifierBlock, self.args[0]).name
    #             if isinstance(self.args[0], ModifierBlock)
    #             else sys.exit("call instr error")
    #         )
    #     )
    #     args: tuple = self.args[1:]
    #     resolved_args = _resolve_call_args(*args, mem=mem, node=node, ir_graph=ir_graph)
    #     resolved_args_types = _resolve_call_args_types(*resolved_args)
    #
    #     fn_header = BaseFnCheck(fn_name=caller, args_types=resolved_args_types)
    #     return args, fn_header


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

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any) -> None:
    #     var: Symbol | ModifierBlock = cast(Symbol | ModifierBlock, self.args[0])
    #     var_type_symbol: Symbol | CompositeSymbol = cast(Symbol | CompositeSymbol, self.args[1])
    #     _declare_variable(var, var_type_symbol, mem, node.irhash, ir_graph)


class AssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        value: SimpleObj | ObjArray | IRBlock,
    ):
        if isinstance(var, Symbol | ModifierBlock) and isinstance(
            value, SimpleObj | ObjArray | IRBlock
        ):
            super().__init__(var, value, name=IRFlag.ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any) -> None:
    #     # TODO: refactor this
    #
    #     var: Symbol = cast(Symbol, self.args[0])
    #     variable = mem.scope.heap[mem.cur_scope].get(var)
    #     mem.scope.stack[mem.cur_scope].push(self.args[1])
    #
    #     # # resolve value to check and assign the correct type
    #     # new_args = _get_assign_datatype(
    #     #     var_type=variable.type,
    #     #     value=value,
    #     #     heap_table=heap_table,
    #     #     types_table=types_table
    #     # )
    #     # # set new arguments
    #     # self.args = (self.args[0], *new_args)
    #
    #     _assign_variable(variable=variable, mem=mem, node=node, ir_graph=ir_graph)


class DeclareAssignInstr(IRInstr):
    def __init__(
        self,
        var: Symbol | ModifierBlock,
        var_type: Symbol | CompositeSymbol | ModifierBlock,
        value: SimpleObj | ObjArray | BaseIRInstr | IRBlock,
    ):
        if (
            isinstance(var, Symbol | ModifierBlock)
            and isinstance(var_type, Symbol | CompositeSymbol | ModifierBlock)
            and isinstance(value, SimpleObj | ObjArray | BaseIRInstr | IRBlock)
        ):
            super().__init__(var, var_type, value, name=IRFlag.DECLARE_ASSIGN)

        else:
            raise ValueError(
                f"var must be symbol, got {type(var)}, "
                f"var type must be symbol or composite symbol, got {type(var_type)} and "
                f"value must be working data or composite working data, got {type(value)}"
            )

    # def resolve(self, mem: MemoryManager, node: IRNode, ir_graph: IRGraph, **_: Any) -> None:
    #     var: Symbol = cast(Symbol, self.args[0])
    #     var_type_symbol: Symbol | CompositeSymbol = cast(Symbol | CompositeSymbol, self.args[1])
    #     _declare_variable(var, var_type_symbol, mem, node.irhash, ir_graph)
    #     variable: DataDef = cast(DataDef, mem.stack.get(var))
    #     mem.stack.push(variable)
    #     _assign_variable(variable=variable, mem=mem, node=node, ir_graph=ir_graph)


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
        ref_table: RefTable,
        ir_module: IRModule,
        **_kwargs: Any,
    ):
        if isinstance(ir_module, IRModule) and isinstance(ref_table, RefTable):
            super().__init__(ref_table, ir_module)

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


# def _declare_variable(
#     var: Symbol | CompositeSymbol | ModifierBlock,
#     var_type_symbol: Symbol | CompositeSymbol,
#     mem: MemoryManager,
#     node_hash: IRHash,
#     ir_graph: IRGraph,
# ) -> None:
#     """
#     Convenient function for resolving variable declaration during the execution execution
#     and store it on the memory for further use.
#
#     Args:
#         var: the actual variable; must be a ``Symbol`` or ``ModifierBlock`` object
#         var_type_symbol:
#         mem: ``MemoryManager`` object
#         node_hash:
#         ir_graph:
#     """
#
#     # we just need the variable for now
#     var_symbol = cast(
#         Symbol | CompositeSymbol, var.args[0] if isinstance(var, ModifierBlock) else var
#     )
#     # TODO: make use of the modifier property through a new code logic later
#
#     if var_symbol in mem.stack:
#         raise ValueError(f"{var_symbol} already in scope memory; cannot re-declare variable")
#
#     var_type = get_type(node_key=node_hash, importing=var_type_symbol, ir_graph=ir_graph)
#
#     match var_type:
#         case None:
#             raise ValueError(
#                 f"var type {var_type} not found on available custom and built-in types"
#             )
#
#         case BaseTypeDef():
#             var_container = var_type(
#                 var_name=var_symbol,
#                 # TODO: use the modifier to define variable flag and define a default as well
#                 flag=VariableKind.MUTABLE,
#             )
#
#             match var_container:
#                 case DataDef():
#                     mem.stack.push(var_container)
#
#                 case _:
#                     raise ValueError(f"{var_container}")
#
#         case _:
#             raise NotImplementedError(
#                 f"{var_type} ({type(var_type)}) not implemented yet for variable declaration"
#             )
#
#
# def _get_assign_datatype(
#     var_type: Symbol | CompositeSymbol,
#     value: SimpleObj | ObjArray | BaseIRInstr | IRBlock,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> Symbol | Literal | Literal | LiteralArray | DataDef:
#     """
#     Convenient function to: (1) check whether the data being assigned to the variable has
#     the correct type, and to (2) resolve any instruction and block.
#
#     For instance, ``int`` data type can be converted to any of the valid integer types,
#     such as ``u64``, ``i64``, so on. However, if the data provided is a ``float`` and the
#     variable is an integer (e.g. ``u64``), it cannot be converted implicitly, so an error
#     will be raised. 'Convertible' data types should be done so explicitly on code,
#     with ``*`` (cast) operation, ex::
#
#         var1:u32 = 4.0*u32
#         var2:f32 = 255*f32
#
#     Data should be prepared to be inserted into the variable container, so any caller or
#     casting should be resolved here.
#
#     Args:
#         var_type: ``CompositeSymbol`` (or ``Symbol``) object of the variable type
#         value: data name as ``WorkingData``, ``CompositeWorkingData``, ``BaseIRInstr`` or
#             ``IRBlock`` object to be assigned to the variable
#         mem: ``MemoryManager`` object
#         node:
#         ir_graph:
#
#     Returns:
#         The data name with adjusted type (if possible) or raise an error, in case data
#          is not compatible
#     """
#
#     new_instr: BaseIRInstr
#
#     match value:
#         case Symbol():
#             res_var = mem.heap[mem.cur_scope].get(value)
#
#             match res_var:
#                 case HeapInvalidKeyError():
#                     raise ValueError(f"variable {value} is not declared yet")
#
#                 case _:
#                     if res_var.type == var_type:
#                         return value
#
#         case CompositeSymbol():
#             raise NotImplementedError("composite symbol on variable assignment not implemented yet")
#
#         case Literal():
#             data_type = (
#                 Symbol(value.type) if isinstance(value.type, str) else CompositeSymbol(value.type)
#             )
#             data_type_tuple = compatible_types.get(data_type, None) or (data_type,)  # type: ignore [arg-type]
#
#             if var_type in data_type_tuple:
#                 dt_ds = builtins_types.get(data_type)  # type: ignore [arg-type]
#
#                 if dt_ds:
#                     mem.symbol.type.add(data_type, dt_ds)
#
#                 else:
#                     raise ValueError(f"invalid type {data_type}")
#
#                 return Literal(value.value, data_type.value)
#
#         case LiteralArray():
#             raise NotImplementedError("composite literal on variable assignment not implemente yet")
#
#         case BaseIRInstr():
#             new_args: tuple[SimpleObj | ObjArray | DataDef] | tuple = ()
#
#             for k in value:
#                 new_args += (
#                     _get_assign_datatype(
#                         var_type=var_type,
#                         value=k,
#                         mem=mem,
#                         node=node,
#                         ir_graph=ir_graph,
#                     ),
#                 )
#
#             new_instr = value.__class__(*new_args, name=value.name)
#             new_instr.resolve(mem, node, ir_graph)
#
#             return mem.scope.stack[mem.cur_scope].pop()
#
#         case BodyBlock() | ArgsBlock() | ArgsValuesBlock():
#             new_blocks: tuple[SimpleObj | ObjArray | DataDef] | tuple = ()
#
#             for k in value:
#                 new_blocks += (
#                     _get_assign_datatype(
#                         var_type=var_type,
#                         value=k,
#                         mem=mem,
#                         node=node,
#                         ir_graph=ir_graph,
#                     ),
#                 )
#
#             new_instr = cast(IRInstr, value.__class__(*new_blocks))
#             new_instr.resolve(mem=mem, node=node, ir_graph=ir_graph)
#
#             return mem.scope.stack[mem.cur_scope].pop()
#
#         case OptionBlock():
#             # FIXME: implement option block
#             raise NotImplementedError()
#
#         case _:
#             raise NotImplementedError(
#                 f"{value} ({type(value)}) on variable assignment with undefined implementation"
#             )
#
#     raise ValueError(f"data {value} to be assigned is not compatible with target type {var_type}")
#
#
# def _assign_variable(
#     *,
#     variable: DataDef,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
#     **arg_values: Any,
# ) -> None:
#     """
#     Convenient function to assign a value to a variable. It calls checks for any
#     data incompatibility and resolvers for any instructions or blocks to be yet
#     evaluated.
#
#     Args:
#         variable: the variable container object
#         mem:
#         node:
#         ir_graph:
#         **arg_values: Any extra argument used
#     """
#
#     args: SimpleObj | ObjArray | BaseIRInstr | IRBlock = mem.scope.stack[mem.cur_scope].pop()
#     new_args: tuple = (
#         _get_assign_datatype(
#             var_type=variable.type,
#             value=args,
#             mem=mem,
#             node=node,
#             ir_graph=ir_graph,
#         ),
#     )
#
#     if len(new_args) > 0 and len(arg_values) == 0:
#         variable.assign(*new_args)
#
#     elif len(new_args) == 0 and len(arg_values) > 0:
#         variable.assign(**arg_values)
#
#     else:
#         raise NotImplementedError(
#             f"should not have arguments and argument-value together when "
#             f"assigning variable {variable}"
#         )
#
#
# def _get_type_from_data(
#     data: DataDef | Literal,
# ) -> Symbol | CompositeSymbol:
#     if isinstance(data, Literal):
#         return data.type
#
#     if isinstance(data, DataDef):
#         return data.type
#
#     sys.exit(f"unknown arg value on call args resolution ({type(data)})")
#
#
# def _resolve_type(
#     data: Symbol | CompositeSymbol | IRBlock | IRInstr,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> BaseTypeDef:
#     """"""
#
#     match data:
#         case Symbol() | CompositeSymbol():
#             res = get_type(node.irhash, data, ir_graph)
#
#             if res:
#                 return res
#
#             raise ValueError(f"type {data} not found")
#
#         case _:
#             raise ValueError(f"unexpected/unknown type {type(data)}")
#
#
# def _resolve_cast(
#     data: DataDef | Literal,
#     to_type: BaseTypeDef,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> None:
#     # cast_op: BaseCastOperator
#
#     if data.is_quantum:
#         if to_type.is_quantum:
#             # cast_op = CastQ2Q(data=data, to_type=to_type, mem=mem, node=node, ir_graph=ir_graph)
#             cast_op: type[CastQ2Q] = CastQ2Q
#
#         else:
#             # cast_op = CastQ2C(data=data, to_type=to_type, mem=mem, node=node, ir_graph=ir_graph)
#             cast_op: type[CastQ2C] = CastQ2C
#
#     else:
#         if to_type.is_quantum:
#             # cast_op = CastC2Q(data=data, to_type=to_type, mem=mem, node=node, ir_graph=ir_graph)
#             cast_op: type[CastC2Q] = CastC2Q
#
#         else:
#             # cast_op = CastC2C(data=data, to_type=to_type, mem=mem, node=node, ir_graph=ir_graph)
#             cast_op: type[CastC2C] = CastC2C
#
#     cast_data = (
#         cast_op(data=data, to_type=to_type, mem=mem, node=node, ir_graph=ir_graph)
#         .flush()
#         .retrieve_cast_data()
#     )
#     mem.stack.push(cast_data)
#
#
# def _resolve_expr_to_data(
#     expr: IRBlock | BaseIRInstr | Symbol | CompositeSymbol | Literal | DataDef,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> Literal | DataDef:
#     """Resolve expression (core literal, symbol, ir block, etc) into actual data"""
#
#     match expr:
#         case IRBlock():
#             res: Literal | DataDef | None = None
#
#             for k in expr:
#                 res = _resolve_expr_to_data(*k, mem=mem, node=node, ir_graph=ir_graph)
#
#             if res:
#                 return res
#
#             raise ValueError("empty ir block on expr to unwrap data")
#
#         case BaseIRInstr():
#             expr.resolve(mem, node, ir_graph)
#             return mem.stack.get_fn_return()
#
#         case Symbol() | CompositeSymbol():
#             return mem.heap.table[mem.heap.last()].get(expr)
#
#         case Literal() | DataDef():
#             return expr
#
#         case _:
#             raise NotImplementedError("could not resolve casting expr to data")
#
#
# def _resolve_call_args(
#     *args: IRBlock | BaseIRInstr | SimpleObj | ObjArray,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> tuple[Literal | DataDef, ...] | tuple:
#     """
#     Convenient function to resolve call arguments.
#
#     Args:
#         *args:
#         mem: ``MemoryManager`` object
#         node:
#         ir_graph:
#     """
#
#     resolved_args: tuple[Symbol | CompositeSymbol, ...] | tuple = ()
#
#     for arg in args:
#         resolved_args += _resolve_expr_to_data(arg, mem, node, ir_graph)
#
#     return resolved_args
#
#
# def _resolve_call_args_types(
#     *args: Literal | DataDef,
# ) -> tuple[Symbol | CompositeSymbol] | tuple:
#     """
#     Resolve types from call arguments
#     """
#
#     resolved_types: tuple[Symbol | CompositeSymbol] | tuple = ()
#
#     for arg in args:
#         match arg:
#             case Literal() | DataDef():
#                 resolved_types += (_get_type_from_data(arg),)
#
#             case _:
#                 raise ValueError(f"unknown arg to retrieve type from ({type(arg)})")
#
#     return resolved_types
#
#
# def _handle_call_instr(
#     fn_header: BaseFnCheck,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
#     flag: IRFlag,
# ) -> None:
#     """
#     Convenient function to handle call instruction and evaluated it.
#
#     Args:
#         fn_header: the caller header (name and arguments types)
#         mem: ``MemoryManager`` object
#         node:
#         ir_graph:
#         flag: ``IRFlag`` enum value
#     """
#
#     match flag:
#         case IRFlag.BUILTIN_FN_CALL:
#             fn_def = get_fn(node_key=node.irhash, importing=fn_header, ir_graph=ir_graph)
#             _resolve_builtin_fn(fn_def=fn_def, mem=mem, node=node, ir_graph=ir_graph)
#
#         case IRFlag.BUILTIN_OPTN_CALL:
#             pass
#
#         case IRFlag.BUILTIN_BDN_CALL:
#             pass
#
#         case IRFlag.BUILTIN_OPTBDN_CALL:
#             pass
#
#         case IRFlag.FN_CALL:
#             args_types: tuple[SimpleObj] | tuple = ()
#             args: tuple[DataDef] | tuple = ()
#
#             mem.stack.new(for_fn_use=True)
#             mem.stack.set_fn_entry()
#
#             fn_header = fn_header[0] if isinstance(fn_header, ModifierBlock) else fn_header
#             fn_entry = BaseFnCheck(fn_name=fn_header, args_types=())
#             fn_def = get_fn(node_key=node.irhash, importing=fn_entry, ir_graph=ir_graph)
#             _resolve_fn_block(
#                 data=cast(IRBlock, fn_def.body), mem=mem, node=node, ir_graph=ir_graph
#             )
#
#             # for _ in range(number_args):
#             #     res = mem.stack.pop()
#             #     args += (res,)
#             #
#             #     if isinstance(res, CoreLiteral):
#             #         args_types += (res.type,)
#             #
#             #     elif isinstance(res, Symbol):
#             #         args_types += (res,)
#             #
#             # # TODO: implement modifier resolution before proceeding on function definition
#             #
#             # caller = caller[0] if isinstance(caller, ModifierBlock) else caller
#             # fn_entry = BaseFnCheck(
#             #     fn_name=caller,
#             #     args_types=args_types,
#             # )
#             # fn_block: IRBlock = cast(IRBlock, mem.symbol.fn.get(fn_entry, None))
#             #
#             # if fn_block is None:
#             #     raise ValueError(
#             #         f"function {caller} with arg type signature {args_types} not found"
#             #     )
#             #
#             # # FIXME: depth_counter value needs to come from the execution global depth counter
#             # fn_scope = mem.new_scope(fn_block, depth_counter=1)
#             # _resolve_fn_block(fn_block, mem, node, ir_graph)
#             # mem.free_last_scope(to_return=True)
#
#         case IRFlag.BDN_CALL:
#             pass
#
#         case IRFlag.OPTBDN_CALL:
#             pass
#     pass
#
#
# def _resolve_builtin_fn(fn_def: FnDef, mem: MemoryManager, node: IRNode, ir_graph: IRGraph) -> None:
#     """
#     Resolve built-in functions. As they do not have ``IRBlock`` or
#     ``IRInstr`` instances, they are treated separated.
#     """
#
#
# def _resolve_fn_block(
#     data: IRBlock | BaseIRInstr | Literal | DataDef,
#     mem: MemoryManager,
#     node: IRNode,
#     ir_graph: IRGraph,
# ) -> None:
#     """
#     Convenient function to resolve function blocks. Whenever it's called from outside,
#     a new scope from ``MemoryManager`` must be created and freed after it finishes
#     execution and return to the outside scope.
#
#     Args:
#         data: IR block or IR instruction object
#         mem: ``MemoryManager`` object
#         node:
#         ir_graph:
#     """
#
#     match data:
#         case ReturnBlock():
#             num_returns = len(data)
#             for k in data:
#                 _resolve_fn_block(k, mem, node, ir_graph)
#
#             for _ in range(num_returns):
#                 mem.stack.set_fn_return(mem.stack.pop())
#
#         case IRBlock():
#             for k in data:
#                 _resolve_fn_block(k, mem, node, ir_graph)
#
#         case BaseIRInstr():
#             data.resolve(mem=mem, node=node, ir_graph=ir_graph)
#
#         case Literal() | DataDef():
#             mem.stack.push(data)
