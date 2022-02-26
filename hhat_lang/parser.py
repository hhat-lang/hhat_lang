try:
    from hhat_lang.core_ast import *
    from hhat_lang.tokens import tokens
except ImportError:
    from core_ast import *
    from tokens import tokens
from rply import ParserGenerator



pg = ParserGenerator(list(tokens.keys()))


@pg.production("program : importing functions main")
def function_0(p):
    return Program(p[1], p[2], p[0])


@pg.production("importing : ")
def function_1(p):
    return Imports()


@pg.production("importing : IMPORTS OPEN import_symbol CLOSE")
def function_2(p):
    return Imports(p[2])


@pg.production("import_symbol : ")
def function_3(p):
    return ImportSymbol()


@pg.production("import_symbol : DSYMBOL import_symbol")
@pg.production("import_symbol : STRING import_symbol")
def function_4(p):
    return ImportSymbol(p[0], p[1])


@pg.production("functions : function functions")
def function_5(p):
    return Functions(p[0], p[1])


@pg.production("functions : ")
def function_6(p):
    return Functions()


@pg.production("function : FUNCTION func_template")
def function_7(p):
    return Function(p[1])


@pg.production("main : MAIN func_template")
def function_8(p):
    return Main(p[1])


@pg.production("main : ")
def function_9(p):
    return Main()


@pg.production("func_template : atype asymbol func_params COLON OPEN func_body func_return CLOSE")
def function_10(p):
    return FuncTempl(p[0], p[1], p[2], p[5], p[6])


@pg.production("atype : NULL_TYPE")
@pg.production("atype : BOOL_TYPE")
@pg.production("atype : INTEGER_TYPE")
@pg.production("atype : FLOAT_TYPE")
@pg.production("atype : STRING_TYPE")
@pg.production("atype : GATES_TYPE")
@pg.production("atype : REGISTER_TYPE")
@pg.production("atype : LIST_TYPE")
@pg.production("atype : HASHMAP_TYPE")
@pg.production("atype : MEAS_TYPE")
def function_11(p):
    return TypeRKW(p[0])


@pg.production("asymbol : SYMBOL")
@pg.production("asymbol : QSYMBOL")
@pg.production("asymbol : PSYMBOL")
def function_12(p):
    return ASymbol(p[0])


@pg.production("func_params : OPEN atype asymbol func_params2 CLOSE")
def function_13(p):
    return FuncParams(p[1], p[2], p[3])


@pg.production("func_params :  ")
def function_14(p):
    return FuncParams()


@pg.production("func_params2 : COMMA atype asymbol func_params2")
def function_15(p):
    return FuncParams(p[1], p[2], p[3])


@pg.production("func_params2 : ")
def function_16(p):
    return FuncParams()


@pg.production("func_body : gen_expr")
def function_17(p):
    return FuncBody(p[0])


@pg.production("func_return : RETURN OPEN value_call_expr2 CLOSE")
@pg.production("func_return : MEASURE OPEN value_call_expr2 CLOSE")
def function_18(p):
    return FuncReturn(p[2])


@pg.production("func_return : ")
def function_19(p):
    return FuncReturn()


@pg.production("gen_expr : data_decl gen_expr")
@pg.production("gen_expr : data_assign gen_expr")
@pg.production("gen_expr : data_call gen_expr")
@pg.production("gen_expr : if_stmt_expr gen_expr")
@pg.production("gen_expr : loop_expr gen_expr")
def function_20(p):
    return GenExpr(p[0], p[1])


@pg.production("gen_expr : ")
def function_21(p):
    return GenExpr()


@pg.production("data_decl : atype asymbol OPEN value_call_expr CLOSE COLON OPEN value_assign CLOSE")
def function_22(p):
    return DataDeclaration(p[0], p[1], p[3], p[7])


@pg.production("data_decl : atype asymbol OPEN value_call_expr CLOSE")
def function_23(p):
    return DataDeclaration(p[0], p[1], p[3])


@pg.production("data_decl : atype asymbol COLON OPEN value_assign CLOSE ")
def function_24(p):
    return DataDeclaration(p[0], p[1], None, p[4])


@pg.production("value_call_expr : INT_NUMBER")
@pg.production("value_call_expr : asymbol")
@pg.production("value_call_expr : data_call")
@pg.production("value_call_expr : FLOAT_NUMBER")
@pg.production("value_call_expr : STRING")
@pg.production("value_call_expr : arkw")
def function_25(p):
    return ValueCallExpr(p[0])


@pg.production("value_assign : extvalue_assign")
def function_26(p):
    return ValueAssign(p[0])


@pg.production("avalue : INT_NUMBER")
@pg.production("avalue : FLOAT_NUMBER")
@pg.production("avalue : STRING")
@pg.production("avalue : asymbol")
def function_27(p):
    return AValue(p[0])


@pg.production("extvalue_assign : opt_assign COLON value_call_expr COMMA extvalue_assign")
def function_28(p):
    return ExtValueAssign(p[2], p[0], p[4])


@pg.production("extvalue_assign : opt_assign COLON value_call_expr")
def function_29(p):
    return ExtValueAssign(p[2], p[0])


@pg.production("opt_assign : ")
def function_30(p):
    return OptAssign()


@pg.production("opt_assign : STAR")
@pg.production("opt_assign : asymbol")
@pg.production("opt_assign : INT_NUMBER")
@pg.production("opt_assign : STRING")
def function_31(p):
    return OptAssign(p[0])


@pg.production("opt_assign : OPEN value_call_expr2 CLOSE")
def function_32(p):
    return OptAssign(p[1])


@pg.production("data_assign : asymbol OPEN value_assign CLOSE")
def function_33(p):
    return DataAssign(p[0], p[2])


@pg.production("data_call : asymbol OPEN value_call_expr2 CLOSE")
@pg.production("data_call : arkw OPEN value_call_expr2 CLOSE")
def function_34(p):
    return DataCall(p[0], p[2])


@pg.production("value_call_expr2 : super_value value_call_expr2 ")
def function_35(p):
    return ValueCallExpr2(p[0], p[1])


@pg.production("value_call_expr2 : COMMA super_value")
def function_36(p):
    return ValueCallExpr2(p[1])


@pg.production("value_call_expr2 : ")
def function_37(p):
    return ValueCallExpr2()


@pg.production("super_value : avalue")
@pg.production("super_value : data_call")
@pg.production("super_value : if_stmt_expr")
@pg.production("super_value : loop_expr")
def function_38(p):
    return SuperValue(p[0])


@pg.production("if_stmt_expr : IF OPEN tests CLOSE COLON OPEN func_body CLOSE elif_stmt_expr else_stmt_expr")
def function_39(p):
    return IfStmtExpr(p[2], p[6], p[8], p[9])


@pg.production("elif_stmt_expr : ELIF OPEN tests CLOSE COLON OPEN func_body CLOSE elif_stmt_expr")
def function_40(p):
    return ElifStmtExpr(p[2], p[6], p[8])


@pg.production("elif_stmt_expr : ")
def function_41(p):
    return ElifStmtExpr()


@pg.production("else_stmt_expr : ELSE COLON OPEN func_body CLOSE")
def function_42(p):
    return ElseStmtExpr(p[3])


@pg.production("else_stmt_expr : ")
def function_43(p):
    return ElseStmtExpr()


@pg.production("loop_expr : FOR asymbol IN loop_range COLON OPEN func_body CLOSE")
def function_44(p):
    return LoopExpr(p[3], p[6], p[1])


@pg.production("loop_expr : FOR loop_range AS asymbol COLON OPEN func_body CLOSE")
def function_45(p):
    return LoopExpr(p[1], p[6], p[3])


@pg.production("loop_expr : FOR loop_range COLON OPEN func_body CLOSE")
def function_46(p):
    return LoopExpr(p[1], p[4])


@pg.production("loop_range : OPEN value_call_expr RANGE value_call_expr CLOSE")
def function_47(p):
    return LoopRange(p[1], p[3])


@pg.production("loop_range : OPEN asymbol CLOSE")
@pg.production("loop_range : OPEN data_call CLOSE")
def function_48(p):
    return LoopRange(p[1])


@pg.production("tests : inside_test append_test tests")
def function_49(p):
    return IfTests(p[0], p[1], p[2])


@pg.production("tests : inside_test")
def function_50(p):
    return IfTests(p[0])


@pg.production("inside_test : bool_value")
def function_51(p):
    return InsideIfTest(p[0])


@pg.production("inside_test : bool_value comparison bool_value")
def function_52(p):
    return InsideIfTest(p[0], p[1], p[2])


@pg.production("bool_value : NOT data_call")
@pg.production("bool_value : NOT avalue")
def function_53(p):
    return BoolValue(p[1], p[0])


@pg.production("bool_value : data_call")
@pg.production("bool_value : avalue")
def function_54(p):
    return BoolValue(p[0])


@pg.production("append_test : AND")
@pg.production("append_test : OR")
def function_55(p):
    return AppendIfTest(p[0])


@pg.production("comparison : EQ")
@pg.production("comparison : GT")
@pg.production("comparison : LT")
@pg.production("comparison : GET")
@pg.production("comparison : LET")
@pg.production("comparison : NEQ")
def function_56(p):
    return ComparisonIfTest(p[0])


@pg.production("arkw : H")
@pg.production("arkw : X")
@pg.production("arkw : Z")
@pg.production("arkw : Y")
@pg.production("arkw : CNOT")
@pg.production("arkw : SWAP")
@pg.production("arkw : CZ")
@pg.production("arkw : RX")
@pg.production("arkw : RZ")
@pg.production("arkw : RY")
@pg.production("arkw : T")
@pg.production("arkw : T_DAG")
@pg.production("arkw : S")
@pg.production("arkw : S_DAG")
@pg.production("arkw : CR")
@pg.production("arkw : TOFFOLI")
@pg.production("arkw : SUPERPOSN")
@pg.production("arkw : AMPLIFICATION")
@pg.production("arkw : RESET")
@pg.production("arkw : ADD")
@pg.production("arkw : MULT")
@pg.production("arkw : DIV")
@pg.production("arkw : POWER")
@pg.production("arkw : LENGTH")
@pg.production("arkw : SQRT")
@pg.production("arkw : INT_SQRT")
@pg.production("arkw : PRINT")
def function_57(p):
    return ARKW(p[0])


parser = pg.build()
