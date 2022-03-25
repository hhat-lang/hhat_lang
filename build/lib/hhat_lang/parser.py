
try:
    from core_ast import (Main, AnyType, AnySymbol, FuncParams,
                          Empty, BodyExprs, AttrDecl, GenericExprs1,
                          AssignValues, AnyCall, InsideCall, AttrAssign,
                          OptAssign, ShortLoopExprs,)
    from tokens import tokens
except ImportError:
    from hhat_lang.core_ast import (Main, AnyType, AnySymbol, FuncParams,
                                    Empty, BodyExprs, AttrDecl, GenericExprs1,
                                    AssignValues, AnyCall, InsideCall, AttrAssign,
                                    OptAssign, ShortLoopExprs,)
    from hhat_lang.tokens import tokens
from rply import ParserGenerator


pg = ParserGenerator(list(tokens.keys()))


@pg.production("main : MAIN any_type any_symbol func_params OPEN body_exprs CLOSE")
def function_0(p):
    return Main(p[1], p[2], p[3], p[5])


@pg.production("any_type : NULL_TYPE")
@pg.production("any_type : BOOL_TYPE")
@pg.production("any_type : INTEGER_TYPE")
@pg.production("any_type : FLOAT_TYPE")
@pg.production("any_type : STR_TYPE")
@pg.production("any_type : GATES_TYPE")
@pg.production("any_type : HASHMAP_TYPE")
@pg.production("any_type : MEAS_TYPE")
def function_1(p):
    return AnyType(p[0])


@pg.production("any_symbol : SYMBOL")
@pg.production("any_symbol : QSYMBOL")
def function_2(p):
    return AnySymbol(p[0])


@pg.production("func_params : OPEN any_type any_symbol func_args CLOSE")
def function_3(p):
    return FuncParams(p[1], p[2], p[3])


@pg.production("func_params : OPEN CLOSE")
def function_4(p):
    return Empty()


@pg.production("func_params : COLON")
def function_5(p):
    return Empty()


@pg.production("func_args : COMMA any_type any_symbol func_args")
def function_6(p):
    return FuncParams(p[1], p[2], p[3])


@pg.production("func_args : ")
def function_7(p):
    return Empty()


@pg.production("body_exprs : attr_decl body_exprs")
@pg.production("body_exprs : attr_assign body_exprs")
@pg.production("body_exprs : attr_call body_exprs")
@pg.production("body_exprs : func_call body_exprs")
def function_8(p):
    return BodyExprs(p[0], p[1])


@pg.production("body_exprs : ")
def function_9(p):
    return Empty()


@pg.production("attr_decl : any_type any_symbol size_decl assign_exprs")
def function_10(p):
    return AttrDecl(p[0], p[1], p[2], p[3])


@pg.production("size_decl : OPEN size_exprs CLOSE")
def function_11(p):
    return GenericExprs1(p[1])


@pg.production("size_decl : ")
def function_12(p):
    return Empty()


@pg.production("size_exprs : INT_LITERAL")
@pg.production("size_exprs : any_symbol")
@pg.production("size_exprs : func_call")
@pg.production("size_exprs : attr_call")
def function_13(p):
    return GenericExprs1(p[0])


@pg.production("assign_exprs : ASSIGN OPEN assign_values CLOSE")
def function_14(p):
    return GenericExprs1(p[2])


@pg.production("assign_exprs : ")
def function_15(p):
    return Empty()


@pg.production("assign_values : opt_assign COLON any_call assign_values2")
@pg.production("assign_values : opt_assign COLON short_loop_exprs assign_values2 ")
def function_16(p):
    return AssignValues(p[0], p[2], p[3])


@pg.production("assign_values2 : COMMA assign_values")
def function_17(p):
    return GenericExprs1(p[1])


@pg.production("assign_values2 : ")
def function_18(p):
    return Empty()


@pg.production("any_call : INT_LITERAL")
@pg.production("any_call : any_symbol")
@pg.production("any_call : FLOAT_LITERAL")
@pg.production("any_call : STR_LITERAL")
@pg.production("any_call : attr_call")
@pg.production("any_call : func_call")
def function_19(p):
    return AnyCall(p[0])


@pg.production("any_call : opt_assign_exprs")
def function_20(p):
    return AnyCall(p[0])


@pg.production("attr_call : any_symbol OPEN call CLOSE")
def function_21(p):
    return InsideCall(p[0], p[2])


@pg.production("func_call : builtin_funcs OPEN call CLOSE")
@pg.production("func_call : other_builtin_funcs OPEN call3 CLOSE")
@pg.production("func_call : special_builtin_funcs OPEN special_call CLOSE")
def function_22(p):
    return InsideCall(p[0], p[2])


@pg.production("func_call : special_builtin_funcs")
@pg.production("func_call : other_builtin_funcs")
def function_23(p):
    return InsideCall(p[0])


@pg.production("other_builtin_funcs : PRINT_BUILTIN")
def function_24(p):
    return InsideCall(p[0])


@pg.production("special_builtin_funcs : OUTPUT_BUILTIN")
@pg.production("special_builtin_funcs : INPUT_BUILTIN")
def function_25(p):
    return InsideCall(p[0])


@pg.production("special_call : assign_values")
def function_26(p):
    return AssignValues(p[0])


@pg.production("call : INT_LITERAL call2")
@pg.production("call : any_symbol call2")
@pg.production("call : func_call call2")
@pg.production("call : attr_call call2")
def function_27(p):
    return AnyCall(p[0], p[1])


@pg.production("call2 : call")
def function_28(p):
    return AnyCall(p[0])


@pg.production("call2 : ")
def function_29(p):
    return Empty()


@pg.production("call3 : INT_LITERAL call4")
@pg.production("call3 : STR_LITERAL call4")
@pg.production("call3 : any_symbol call4")
@pg.production("call3 : func_call call4")
@pg.production("call3 : attr_call call4")
def function_30(p):
    return AnyCall(p[0], p[1])


@pg.production("call4 : call3")
def function_31(p):
    return AnyCall(p[0])


@pg.production("call4 : ")
def function_32(p):
    return Empty()


@pg.production("attr_assign : any_symbol OPEN assign_values CLOSE")
def function_33(p):
    return AttrAssign(p[0], p[2])


@pg.production("opt_assign : ")
def function_34(p):
    return OptAssign()


@pg.production("opt_assign : STAR")
@pg.production("opt_assign : any_symbol")
@pg.production("opt_assign : INT_LITERAL")
@pg.production("opt_assign : STR_LITERAL")
@pg.production("opt_assign : opt_assign_exprs")
@pg.production("opt_assign : short_loop_exprs")
def function_35(p):
    return OptAssign(p[0])


@pg.production("builtin_funcs : H_GATE")
@pg.production("builtin_funcs : X_GATE")
@pg.production("builtin_funcs : Z_GATE")
@pg.production("builtin_funcs : Y_GATE")
@pg.production("builtin_funcs : CNOT_GATE")
@pg.production("builtin_funcs : SWAP_GATE")
@pg.production("builtin_funcs : CZ_GATE")
@pg.production("builtin_funcs : RX_GATE")
@pg.production("builtin_funcs : RZ_GATE")
@pg.production("builtin_funcs : RY_GATE")
@pg.production("builtin_funcs : T_GATE")
@pg.production("builtin_funcs : T_DAG_GATE")
@pg.production("builtin_funcs : S_GATE")
@pg.production("builtin_funcs : S_DAG_GATE")
@pg.production("builtin_funcs : CR_GATE")
@pg.production("builtin_funcs : TOFFOLI_GATE")
@pg.production("builtin_funcs : SUPERPOSN_GATE")
@pg.production("builtin_funcs : AMPLIFICATION_GATE")
@pg.production("builtin_funcs : RESET_GATE")
@pg.production("builtin_funcs : ADD_BUILTIN")
@pg.production("builtin_funcs : SUB_BUILTIN")
@pg.production("builtin_funcs : MULT_BUILTIN")
@pg.production("builtin_funcs : DIV_BUILTIN")
@pg.production("builtin_funcs : POWER_BUILTIN")
@pg.production("builtin_funcs : SQRT_BUILTIN")
def function_36(p):
    return InsideCall(p[0])


@pg.production("opt_assign_exprs : OPEN call call2 CLOSE")
def function_37(p):
    return AnyCall(p[1], p[2])


@pg.production("short_loop_exprs : loop_range RANGE_LOOP loop_range")
def function_38(p):
    return ShortLoopExprs(p[0], p[2])


@pg.production("loop_range : INT_LITERAL")
@pg.production("loop_range : SYMBOL")
@pg.production("loop_range : attr_call")
@pg.production("loop_range : func_call")
def function_39(p):
    return GenericExprs1(p[0])


parser = pg.build()
