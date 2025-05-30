# type: ignore
"""
In this file there are three distinct sections:

1. The building functions to get from AST to something that IR and the IR tables can handle;
2. The actual IR tables builders, namely types and functions; and
3. The main code builder where the `main` closure lies.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ast import AST
from hhat_lang.core.data.core import (
    CompositeSymbol,
    CoreLiteral,
    Symbol,
)
from hhat_lang.dialects.heather.code.ast import (
    ArgTypePair,
    ArgValuePair,
    Array,
    Assign,
    Body,
    BodyType,
    Call,
    CallArgs,
    CallWithBody,
    CallWithBodyOptions,
    Cast,
    CompositeId,
    CompositeIdWithClosure,
    Declare,
    DeclareAssign,
    EnumTypeMember,
    Expr,
    FnArgs,
    FnDef,
    FnImport,
    Hash,
    Id,
    Imports,
    InsideOption,
    Literal,
    Main,
    MethodCall,
    MethodCallArgs,
    ModifiedId,
    Modifier,
    OnlyValue,
    Program,
    SingleTypeMember,
    TypeDef,
    TypeImport,
    TypeMember,
    TypeType,
    ValueType,
)
from hhat_lang.dialects.heather.code.simple_ir_builder.builder import (
    define_argvaluepair,
    define_compositeid,
    define_id,
    define_literal,
)

# for now just a simple IR for the interpreter suffices
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IR
from hhat_lang.dialects.heather.parsing.imports import (
    parse_imports,
    parse_types,
    parse_types_compositeid,
    parse_types_compositeidwithclosure,
)

# TODO: include other implementation modules for the IR, as below.
#  - each one of them should contain all the named functions
#  - the correct IR module should be read from some configuration file
"""
from hhat_heather.code.mlir_ir import define_id
...
"""


########################################################
# FUNCTION BUILDERS FROM AST TO ACTUAL CODE FOR THE IR #
########################################################


def _build_id(code: Id) -> Symbol:
    return define_id(code)


def _build_compositeid(code: CompositeId) -> CompositeSymbol:
    return define_compositeid(code)


def _build_argvaluepair(code: ArgValuePair) -> tuple[Symbol, Any]:
    return define_argvaluepair(code)


def _build_onlyvalue(code: OnlyValue) -> Symbol | CompositeSymbol | CoreLiteral | Any:
    return _build_valuetype(code.value[0])


def _build_modifier(code: Modifier) -> tuple[tuple[Symbol, Any], ...]:
    mods = ()

    for mod in code.value:

        arg, value = _build_argvaluepair(mod)
        mods += ((arg, value),)

    return mods


def _build_modifiedid(code: ModifiedId) -> Any:
    pass


def _build_literal(code: Literal) -> CoreLiteral:
    return define_literal(code)


def _build_array(code: Array) -> Any:
    pass


def _build_hash(code: Hash) -> Any:
    pass


def _build_expr(code: Expr) -> Any:
    pass


def _build_declare(code: Declare) -> Any:
    var_name = _build_id(code.value[0])
    var_type = _build_typetype(code.value[1])


def _build_assign(code: Assign) -> Any:
    pass


def _build_declareassign(code: DeclareAssign) -> Any:
    pass


def _build_callargs(code: CallArgs) -> Any:
    pass


def _build_call(code: Call) -> Any:
    pass


def _build_methodcallargs(code: MethodCallArgs) -> Any:
    pass


def _build_methodcall(code: MethodCall) -> Any:
    pass


def _build_insideoption(code: InsideOption) -> Any:
    pass


def _build_callwithbodyoptions(code: CallWithBodyOptions) -> Any:
    pass


def _build_callwithbody(code: CallWithBody) -> Any:
    pass


def _build_argtypepair(code: ArgTypePair) -> tuple[Symbol, Any]:
    pass


def _build_fnargs(code: FnArgs) -> Any:
    pass


def _build_fndef(code: FnDef) -> Any:
    pass


def _build_typemember(code: TypeMember) -> Any:
    pass


def _build_singletypemember(code: SingleTypeMember) -> Any:
    pass


def _build_enumtypemember(code: EnumTypeMember) -> Any:
    pass


def _build_typedef(code: TypeDef) -> Any:
    pass


def _build_typeimport(code: TypeImport) -> Any:
    for k in code:

        match k:
            case Id():
                pass

            case CompositeId():
                res = parse_types_compositeid(k)

            case CompositeIdWithClosure():
                res = parse_types_compositeidwithclosure(k)


def _build_fnimport(code: FnImport) -> Any:
    pass


def _build_imports(code: Imports) -> Any:
    for k in code:

        match k:
            case TypeImport():
                return _build_typeimport(k)

            case FnImport():
                return _build_fnimport(k)

            case _:
                raise ValueError(f"invalid import syntax\n  =>\n{k}\n")


def _build_body(code: Body) -> Any:
    for k in code:

        _build_bodytype(k)


##############################
# TYPES DESCRIPTORS BUILDERS #
##############################


def _build_valuetype(code: ValueType) -> Any:
    """Build based on the `ValueType` type descriptor."""

    match tmp := code:

        case Id():
            return _build_id(tmp)

        case CompositeId():
            return _build_compositeid(tmp)

        case ModifiedId():
            return _build_modifiedid(tmp)

        case Literal():
            return _build_literal(tmp)

        case Array():
            raise NotImplementedError("array not implemented")

        case Hash():
            raise NotImplementedError("hash not implemented")

        case _:
            raise ValueError(f"unknown '{code}'.")


def _build_typetype(code: TypeType) -> Any:
    """Build based on the `TypeType` type descriptor."""

    match code:
        case Id():
            return _build_id(code)

        case CompositeId():
            return _build_compositeid(code)

        case ModifiedId():
            return _build_modifiedid(code)

        case _:
            raise NotImplementedError()


def _build_bodytype(code: BodyType) -> Any:
    """Build based on the `BodyType` type descriptor."""

    match k := code:
        case Expr():
            _build_expr(k)

        case Declare():
            _build_declare(k)

        case Assign():
            _build_assign(k)

        case DeclareAssign():
            _build_declareassign(k)

        case Call():
            _build_call(k)

        case MethodCall():
            _build_methodcall(k)

        case CallWithBody():
            _build_callwithbody(k)

        case CallWithBodyOptions():
            _build_callwithbodyoptions(k)


##################
# TABLE BUILDERS #
##################


def build_typetable(code: AST) -> Any:
    for k in code:

        match k:

            case Id():
                pass

            case CompositeId():
                pass

            case ArgValuePair():
                pass

            case OnlyValue():
                pass

            case Modifier():
                pass

            case ModifiedId():
                pass

            case Literal():
                pass

            case Array():
                pass

            case Hash():
                pass

            case Expr():
                pass

            case Declare():
                pass

            case Assign():
                pass

            case DeclareAssign():
                pass

            case CallArgs():
                pass

            case Call():
                pass

            case MethodCallArgs():
                pass

            case MethodCall():
                pass

            case InsideOption():
                pass

            case CallWithBodyOptions():
                pass

            case CallWithBody():
                pass

            case ArgTypePair():
                pass

            case FnArgs():
                pass

            case TypeMember():
                pass

            case TypeDef():
                pass

            case Imports():
                pass

            case Body():
                pass

            case Main():
                pass

            case Program():
                pass

            case _:
                raise NotImplementedError()


def build_fntable(code: AST) -> Any:
    fn_name = code.value[0]
    fn_type = code.value[1]
    fn_args = _build_fnargs(code.value[2])
    fn_body = _build_body(code.value[3])


#############
# MAIN CODE #
#############


def build_main(code: AST) -> Any:
    ir = IR()

    for k in code:

        match k:

            case Imports():
                res = parse_imports(k)

            case Body():
                pass

            case Main():
                pass

            case Program():
                pass

            case _:
                raise NotImplementedError()
