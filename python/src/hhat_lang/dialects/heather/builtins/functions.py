from __future__ import annotations

from typing import Any, Callable
from importlib import import_module

from hhat_lang.core.builtin.quantum_instr import BaseQuantumInstr
from hhat_lang.core.fn_system.base import BaseFunctionData
from hhat_lang.core.memory.manager import MemoryManager
from hhat_lang.core.type_system import FullName, NameSpace
from hhat_lang.core.utils.dialect_descriptor import get_dialect_data
from hhat_lang.dialect_builder.builtins.functions import ArgsWildCard, any_type, any_q__type
from hhat_lang.dialect_builder.builtins.types import (
    uint_types,
    sint_types,
    q__uint_types, null_type, q__u2_type,
)
from hhat_lang.dialects.heather import DIALECT_PATH
from hhat_lang.dialects.heather.interpreter.evaluate import Evaluate
from hhat_lang.dialects.heather.syntax.base import Literal

# TODO: implement it properly without hardcoding it
QUANTUM_INSTR = import_module(
    "hhat_lang.quantum_lowlevel.qiskit.frontend.openqasm.v2.quantum_instr"
)


def fn_print(
    *,
    mem: MemoryManager,
    args: Any,
    evaluate: Evaluate,
    **kwargs: Any
) -> Any:
    print(f"[PRINT]", *args, **kwargs)
    return Literal(
        value="null",
        lit_type="null",
        dialect=get_dialect_data(dialect_dir=DIALECT_PATH, dialect_name="heather")
    )


def fn_cast(
    *,
    mem: MemoryManager,
    data: Any,
    evaluate: Evaluate,
    to: FullName | None = None,
    **kwargs: Any
) -> Any:
    match data:
        case _:
            pass

    match to.name:
        case "u16":
            pass

        case "u32":
            pass

        case "u64":
            pass

        case "char":
            pass

        case "str":
            pass

        case "f32":
            pass

        case "f64":
            pass

        case _:
            raise NotImplementedError(f"{to.name} not implemented")


def fn_add(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_sub(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_times(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_div(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_pow(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_mod(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_q__redim(*, mem: MemoryManager, args: Any, evaluate: Evaluate, **kwargs: Any) -> Any:
    match args:
        case Literal():
            if args.type == "@int":
                pass
            elif args.type in q__uint_types:
                pass

    res: BaseQuantumInstr = QUANTUM_INSTR.QRedim()
    _instr = res.apply(idxs=args, mem=mem, evaluate=evaluate).get_instr()
    mem.stack.put(_instr, block=False)
    print(f" [fn=>in] stack: {mem.stack.queue}")
    return


def fn_q__sync(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


def fn_q__add(mem: MemoryManager, *args: Any, **kwargs: Any) -> None:
    pass


class BuiltinFunctionData(BaseFunctionData):
    def __call__(self, *, callback: Callable) -> Callable:
        return callback


"""
Defines the built-in functions, where the first key is the function `FullName` (namespace + id);
inside there is another dictionary that contain a tuple of values, where the first item is the
function type and the second is the function args, both as `FullName` instances.
Inside there's the actual `BuiltinFunctionData` instance defining the corresponding function.
"""
print_fn = FullName(NameSpace(), "print")
cast_fn = FullName(NameSpace(), "cast")
add_fn = FullName(NameSpace(), "add")
q__redim_fn = FullName(NameSpace(), "@redim")

# functions objects with keys as FullName and values as BuiltinFunctionData callables
functions_dict = {
    # print function
    print_fn: {
        (null_type.name, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(print_fn)
            .add_type(null_type.name)
            .add_args()(callback=fn_print)
        ),
    },
    # cast function
    cast_fn: {
        (any_type.name, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(cast_fn)
            .add_type(any_type.name)
            .add_args()(callback=fn_cast)
        )
    },
    # add function
    add_fn: {
        (any_type.name, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(add_fn)
            .add_type(any_type.name)
            .add_args()(callback=fn_add)
        )
    },
    # @redim function
    q__redim_fn: {
        (any_q__type.name, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(q__redim_fn)
            .add_type(any_q__type.name)
            .add_args()(callback=fn_q__redim)
        )
    }
}
