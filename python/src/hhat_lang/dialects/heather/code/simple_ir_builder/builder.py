# type: ignore

from __future__ import annotations

from typing import Any, cast

from hhat_lang.core.code.utils import check_quantum_type_correctness
from hhat_lang.core.data.core import CompositeSymbol, CoreLiteral, Symbol
from hhat_lang.dialects.heather.code.ast import (
    ArgValuePair,
    Array,
    Assign,
    CompositeId,
    Declare,
    DeclareAssign,
    Hash,
    Id,
    Literal,
    ModifiedId,
    ValueType,
)

#########################
# IR DEFINING FUNCTIONS #
#########################


def define_id(code: Id) -> Symbol:
    name: str = cast(str, code.value[0])
    return Symbol(name)


def define_compositeid(code: CompositeId) -> CompositeSymbol:
    names: tuple[str, ...] = cast(tuple, code.value)
    check_quantum_type_correctness(names)
    return CompositeSymbol(names)


def define_literal(code: Literal) -> CoreLiteral:
    value = cast(str, code.value[0])
    return CoreLiteral(value, code.name)


def define_argvaluepair(code: ArgValuePair) -> tuple[Symbol, Any]:
    arg_name = cast(Id, code.value[0])
    arg = define_id(arg_name)

    value = define_valuetype(code.value[1])

    return arg, value


def define_valuetype(code: ValueType) -> Any:
    match code:

        case Id():
            return define_id(code)

        case CompositeId():
            return define_compositeid(code)

        case Literal():
            return define_literal(code)

        case ModifiedId():
            raise NotImplementedError()

        case Array():
            raise NotImplementedError()

        case Hash():
            raise NotImplementedError()

        case _:
            raise ValueError(f"unknown '{code}'.")


def define_declare(code: Declare) -> Any:
    pass


def define_assign(code: Assign) -> Any:
    pass


def define_declareassign(code: DeclareAssign) -> Any:
    pass
