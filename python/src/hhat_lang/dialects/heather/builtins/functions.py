from __future__ import annotations

from typing import Any, Callable
from importlib import import_module

from hhat_lang.core.fn_system.base import BaseFunctionData
from hhat_lang.core.memory.manager import MemoryManager
from hhat_lang.core.type_system import FullName, NameSpace
from hhat_lang.core.utils.dialect_descriptor import get_dialect_data
from hhat_lang.dialect_builder.builtins.functions import ArgsWildCard
from hhat_lang.dialect_builder.builtins.types import null_type
from hhat_lang.dialects.heather import DIALECT_PATH
from hhat_lang.dialects.heather.syntax.base import Literal

# TODO: implement it properly without harcode
QUANTUM_INSTR = import_module(
    "hhat_lang.quantum_lowlevel.qiskit.frontend.openqasm.v2.quantum_instr"
)


def fn_print(*, mem: MemoryManager, args: Any, **kwargs: Any) -> Any:
    print(f"[PRINT]", *args, **kwargs)
    return Literal(
        value="null",
        lit_type="null",
        dialect=get_dialect_data(dialect_dir=DIALECT_PATH, dialect_name="heather")
    )


def fn_cast(*, mem: MemoryManager, data: Any, to: FullName | None = None, **kwargs: Any) -> Any:
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


def fn_q__redim(*, mem: MemoryManager, args: Any, **kwargs: Any) -> None:
    res = QUANTUM_INSTR.q__redim(mem=mem, idxs=args, **kwargs)
    mem.stack.put(res, block=False)
    print(f" [fn=>in] stack: {mem.stack.queue}")


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
print_name = FullName(NameSpace(), "print")
cast_name = FullName(NameSpace(), "cast")
add_name = FullName(NameSpace(), "add")
q__redim_name = FullName(NameSpace(), "@redim")

functions_dict = {
    # print function, type null with any type of arguments
    print_name: {
        (FullName(NameSpace(), "null"), ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(print_name)
            .add_type()
            .add_args()(callback=fn_print)
        ),
    },
    # cast function
    cast_name: {
        (None, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(cast_name)
            .add_type()
            .add_args()(callback=fn_cast)
        )
    },
    # add function
    add_name: {
        (None, ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(add_name)
            .add_type()
            .add_args()(callback=fn_add)
        )
    },
    # @redim function
    q__redim_name: {
        (FullName(NameSpace(), "@u2"), ArgsWildCard()): (
            BuiltinFunctionData()
            .add_name(q__redim_name)
            .add_type()
            .add_args()(callback=fn_q__redim)
        )
    }
}
