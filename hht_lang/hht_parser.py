from hht_lang.hht_core_ast import *
from rply import ParserGenerator
from hht_lang.hht_tokens import tokens


pg = ParserGenerator(list(tokens.keys()))


@pg.production("program : gen_expr gen_expr")
def function_0(p):
    return Program(p[0], p[1])


@pg.production("gen_expr : data_dec")
def function_1(p):
    return GenExpr(p[0])


@pg.production("gen_expr : data_assign")
def function_2(p):
    return GenExpr(p[0])


@pg.production("gen_expr : data_ret")
def function_3(p):
    return GenExpr(p[0])


@pg.production("gen_expr : ")
def function_4(p):
    return GenExpr()


@pg.production("data_dec : atype SYMBOL size_dec value_expr")
def function_5(p):
    return DataDeclaration(p[0], p[1], p[2], p[3])


@pg.production("size_dec : OPEN value_ret CLOSE")
def function_6(p):
    return SizeDeclaration(p[1])


@pg.production("size_dec : ")
def function_7(p):
    return SizeDeclaration()


@pg.production("value_expr : COLON OPEN value CLOSE")
def function_8(p):
    return ValueExpr(p[2])


@pg.production("value_expr : ")
def function_9(p):
    return ValueExpr()


@pg.production("value : value_assign")
@pg.production("value : INT_NUMBER")
@pg.production("value : FLOAT_NUMBER")
@pg.production("value : STRING")
@pg.production("value : SYMBOL")
def function_10(p):
    return Value(p[0])


@pg.production("data_assign : SYMBOL value_expr")
def function_11(p):
    return DataAssignment(p[0], p[1])


@pg.production("value_assign : opt_assign COLON value_ret value_assign")
def function_12(p):
    return ValueAssign(p[0], p[2], p[3])


@pg.production("value_assign : opt_assign COLON value_ret")
def function_13(p):
    return ValueAssign(p[0], p[2])


@pg.production("expr_assign : OPEN opt_assign COLON value inner_assign CLOSE")
def function_14(p):
    return ExprAssign(p[3], p[1], p[4])


@pg.production("inner_assign : opt_assign COLON value")
def function_15(p):
    return InnerAssign(p[2], p[0])


@pg.production("inner_assign : ")
def function_16(p):
    return InnerAssign()


@pg.production("opt_assign : STAR")
@pg.production("opt_assign : SYMBOL")
@pg.production("opt_assign : INT_NUMBER")
@pg.production("opt_assign : STRING")
def function_17(p):
    return OptionalAssign(p[0])


@pg.production("opt_assign : ")
def function_18(p):
    return OptionalAssign()


@pg.production("data_ret : SYMBOL OPEN value_ret CLOSE")
def function_19(p):
    return DataRetrieval()


@pg.production("value_ret : INT_NUMBER")
@pg.production("value_ret : FLOAT_NUMBER")
@pg.production("value_ret : STRING")
@pg.production("value_ret : SYMBOL")
def function_20(p):
    return ValueRetrieval(p[0])


@pg.production("atype : NULL_TYPE")
@pg.production("atype : BOOL_TYPE")
@pg.production("atype : INTEGER_TYPE")
@pg.production("atype : FLOAT_TYPE")
@pg.production("atype : STRING_TYPE")
@pg.production("atype : REGISTER_TYPE")
def function_21(p):
    return TypeRKW(p[0])


parser = pg.build()
