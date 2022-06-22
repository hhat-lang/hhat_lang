
try:
    from new_ast import (Program, Function, FuncTemplate, Params,
                          AType, ASymbol, AQSymbol, Body,
                          AttrDecl, Expr, ManyExprs, Entity,
                          AttrAssign, Call, Func, ABuiltIn,
                          IfStmt, ElifStmt, ElseStmt, Tests,
                          ForLoop,)
    from tokens import tokens
except ImportError:
    from hhat_lang.new_ast import (Program, Function, FuncTemplate, Params,
                                    AType, ASymbol, AQSymbol, Body,
                                    AttrDecl, Expr, ManyExprs, Entity,
                                    AttrAssign, Call, Func, ABuiltIn,
                                    IfStmt, ElifStmt, ElseStmt, Tests,
                                    ForLoop,)
    from hhat_lang.tokens import tokens
from rply import ParserGenerator


pg = ParserGenerator(list(tokens.keys()))


@pg.production("program : funcs main")
def function_0(p):
    return Program(p[0], p[1])


@pg.production("funcs : ")
def function_1(p):
    return Function()


@pg.production("funcs : FUNCTION func_template funcs")
def function_2(p):
    return Function(p[0], p[1], p[2])


@pg.production("main : ")
def function_3(p):
    return Function()


@pg.production("main : MAIN func_template")
def function_4(p):
    return Function(p[0], p[1])


@pg.production("func_template : type symbol params OPEN body result CLOSE")
def function_5(p):
    return FuncTemplate(p[0], p[1], p[2], p[4], p[5])


@pg.production("params : OPEN type symbol func_params CLOSE")
def function_6(p):
    return Params(p[1], p[2], p[3])


@pg.production("params : OPEN CLOSE")
def function_7(p):
    return Params()


@pg.production("params : COLON")
def function_8(p):
    return Params()


@pg.production("func_params : COMMA type symbol func_params")
def function_9(p):
    return Params(p[1], p[2], p[3])


@pg.production("func_params : ")
def function_10(p):
    return Params()


@pg.production("type : NULL_TYPE")
@pg.production("type : BOOL_TYPE")
@pg.production("type : INT_TYPE")
@pg.production("type : FLOAT_TYPE")
@pg.production("type : STR_TYPE")
@pg.production("type : CIRCUIT_TYPE")
@pg.production("type : HASHMAP_TYPE")
@pg.production("type : MEASUREMENT_TYPE")
@pg.production("type : symbol")
def function_11(p):
    return AType(p[0])


@pg.production("symbol : SYMBOL")
def function_12(p):
    return ASymbol(p[0])


@pg.production("symbol : QSYMBOL")
def function_13(p):
    return AQSymbol(p[0])


@pg.production("body : attr_decl body")
def function_14(p):
    return Body(p[0], p[1])


@pg.production("body : attr_assign body")
def function_15(p):
    return Body(p[0], p[1])


@pg.production("body : generic_call body")
def function_16(p):
    return Body(p[0], p[1])


@pg.production("body : if_stmt body")
def function_17(p):
    return Body(p[0], p[1])


@pg.production("body : for_loop body")
def function_18(p):
    return Body(p[0], p[1])


@pg.production("body : ")
def function_19(p):
    return Body()


@pg.production("attr_decl : type symbol")
def function_20(p):
    return AttrDecl(p[0], p[1])


@pg.production("attr_decl : type OPEN expr CLOSE symbol")
def function_21(p):
    return AttrDecl(p[0], p[4], p[2])


@pg.production("attr_decl : type OPEN expr CLOSE symbol ASSIGN attr_decl_assign")
def function_22(p):
    return AttrDecl(p[0], p[4], p[2], p[6])


@pg.production("attr_decl : type symbol ASSIGN attr_decl_assign")
def function_23(p):
    return AttrDecl(p[0], p[1], None, p[3])


@pg.production("expr : INT_LITERAL")
def function_24(p):
    return Expr(p[0])


@pg.production("expr : STR_LITERAL")
def function_25(p):
    return Expr(p[0])


@pg.production("expr : FLOAT_LITERAL")
def function_26(p):
    return Expr(p[0])


@pg.production("expr : TRUE_LITERAL")
def function_27(p):
    return Expr(p[0])


@pg.production("expr : FALSE_LITERAL")
def function_28(p):
    return Expr(p[0])


@pg.production("expr : symbol_call")
def function_29(p):
    return Expr(p[0])


@pg.production("expr : generic_call")
def function_30(p):
    return Expr(p[0])


@pg.production("expr : expr RANGE_LOOP expr")
def function_31(p):
    return Expr(p[0], p[2])


@pg.production("expr : inline_func")
def function_32(p):
    return Expr(p[0])


@pg.production("attr_decl_assign : OPEN entity more_entity CLOSE")
def function_33(p):
    return ManyExprs(p[1], p[2])


@pg.production("more_entity : COMMA entity more_entity")
def function_34(p):
    return ManyExprs(p[1], p[2])


@pg.production("more_entity : ")
def function_35(p):
    return ManyExprs()


@pg.production("entity : expr COLON expr")
def function_36(p):
    return Entity(p[0], p[2])


@pg.production("entity : COLON expr")
def function_37(p):
    return Entity(p[1])


@pg.production("attr_assign : symbol attr_decl_assign")
def function_38(p):
    return AttrAssign(p[0], p[1])


@pg.production("symbol_call : symbol OPEN more_expr CLOSE")
def function_39(p):
    return Call(p[0], p[2])


@pg.production("symbol_call : symbol")
def function_40(p):
    return Expr(p[0])


@pg.production("generic_call : func")
def function_41(p):
    return Call(p[0])


@pg.production("generic_call : func OPEN more_expr CLOSE")
def function_42(p):
    return Call(p[0], p[2])


@pg.production("func : reserved_keyword")
def function_43(p):
    return Func(p[0])


@pg.production("func : q_keyword")
def function_44(p):
    return Func(p[0])


@pg.production("func : logic_ops")
def function_45(p):
    return Func(p[0])


@pg.production("reserved_keyword : ADD_BUILTIN")
@pg.production("reserved_keyword : SUB_BUILTIN")
@pg.production("reserved_keyword : MULT_BUILTIN")
@pg.production("reserved_keyword : DIV_BUILTIN")
@pg.production("reserved_keyword : POWER_BUILTIN")
@pg.production("reserved_keyword : SQRT_BUILTIN")
@pg.production("reserved_keyword : INPUT_BUILTIN")
@pg.production("reserved_keyword : OUTPUT_BUILTIN")
def function_46(p):
    return ABuiltIn(p[0])


@pg.production("q_keyword : H_GATE")
@pg.production("q_keyword : X_GATE")
@pg.production("q_keyword : Z_GATE")
@pg.production("q_keyword : Y_GATE")
@pg.production("q_keyword : CNOT_GATE")
@pg.production("q_keyword : SWAP_GATE")
@pg.production("q_keyword : CZ_GATE")
@pg.production("q_keyword : RX_GATE")
@pg.production("q_keyword : RZ_GATE")
@pg.production("q_keyword : RY_GATE")
@pg.production("q_keyword : T_GATE")
@pg.production("q_keyword : T-DAG_GATE")
@pg.production("q_keyword : S_GATE")
@pg.production("q_keyword : S-DAG_GATE")
@pg.production("q_keyword : CR_GATE")
@pg.production("q_keyword : TOFFOLI_GATE")
@pg.production("q_keyword : INIT_GATE")
@pg.production("q_keyword : SUPERPOSN_GATE")
@pg.production("q_keyword : AMPLIFICATION_GATE")
@pg.production("q_keyword : RESET_GATE")
@pg.production("q_keyword : SYNC_GATE")
@pg.production("q_keyword : AND_GATE")
@pg.production("q_keyword : OR_GATE")
@pg.production("q_keyword : PRINT_BUILTIN")
def function_47(p):
    return ABuiltIn(p[0])


@pg.production("inline_func : OPEN expr more_expr CLOSE")
def function_48(p):
    return ManyExprs(p[1], p[2])


@pg.production("more_expr : expr more_expr")
def function_49(p):
    return ManyExprs(p[0], p[1])


@pg.production("more_expr : ")
def function_50(p):
    return ManyExprs()


@pg.production("if_stmt : IF_COND OPEN tests CLOSE COLON OPEN body CLOSE elif_stmt else_stmt")
def function_51(p):
    return IfStmt(p[2], p[6], p[8], p[9])


@pg.production("elif_stmt : ELIF_COND OPEN tests CLOSE COLON OPEN body CLOSE elif_stmt")
def function_52(p):
    return ElifStmt(p[2], p[6], p[8])


@pg.production("elif_stmt : ")
def function_53(p):
    return ElifStmt()


@pg.production("else_stmt : ELSE_COND COLON OPEN body CLOSE")
def function_54(p):
    return ElseStmt(p[3])


@pg.production("else_stmt : ")
def function_55(p):
    return ElseStmt()


@pg.production("tests : logic_ops_call OPEN expr more_expr CLOSE")
def function_56(p):
    return Tests(p[0], p[2], p[3])


@pg.production("logic_ops_call : logic_ops")
def function_57(p):
    return Call(p[0])


@pg.production("logic_ops : AND_LOGOP")
@pg.production("logic_ops : OR_LOGOP")
@pg.production("logic_ops : NOT_LOGOP")
@pg.production("logic_ops : EQ_OP")
@pg.production("logic_ops : GT_OP")
@pg.production("logic_ops : GTE_OP")
@pg.production("logic_ops : LT_OP")
@pg.production("logic_ops : LTE_OP")
@pg.production("logic_ops : NEQ_OP")
def function_58(p):
    return ABuiltIn(p[0])


@pg.production("for_loop : FOR_LOOP OPEN expr CLOSE OPEN entity more_entity CLOSE")
def function_59(p):
    return ForLoop(p[2], p[5], p[6])


@pg.production("result : RETURN OPEN expr more_expr CLOSE")
def function_60(p):
    return ManyExprs(p[2], p[3], p[0])


@pg.production("result : ")
def function_61(p):
    return ManyExprs()


parser = pg.build()
