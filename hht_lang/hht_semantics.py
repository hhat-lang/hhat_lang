from hht_core_ast import *

s = [
    ("program : gen_expr gen_expr", Program, [0, 1]),
    ("gen_expr : data_dec", GenExpr, [0]),
    ("gen_expr : data_assign", GenExpr, [0]),
    ("gen_expr : data_ret", GenExpr, [0]),
    ("gen_expr : ", GenExpr, []),
    ("data_dec : atype SYMBOL size_dec value_expr", DataDeclaration, [0, 1, 2, 3]),
    ("size_dec : OPEN value_ret CLOSE", SizeDeclaration, [1]),
    ("size_dec : ", SizeDeclaration, []),
    ("value_expr : COLON OPEN value CLOSE", ValueExpr, [2]),
    ("value_expr : ", ValueExpr, []),
    ("value : value_assign | INT_NUMBER | FLOAT_NUMBER | STRING | SYMBOL", Value, [0]),
    ("data_assign : SYMBOL value_expr", DataAssignment, [0, 1]),
    ("value_assign : opt_assign COLON value_ret value_assign", ValueAssign, [0, 2, 3]),
    ("value_assign : opt_assign COLON value_ret", ValueAssign, [0, 2]),
    ("expr_assign : OPEN opt_assign COLON value inner_assign CLOSE", ExprAssign, [3, 1, 4]),
    ("inner_assign : opt_assign COLON value", InnerAssign, [2, 0]),
    ("inner_assign : ", InnerAssign, []),
    ("opt_assign : STAR | SYMBOL | INT_NUMBER | STRING", OptionalAssign, [0]),
    ("opt_assign : ", OptionalAssign, []),
    ("data_ret : SYMBOL OPEN value_ret CLOSE", DataRetrieval, []),
    ("value_ret : INT_NUMBER | FLOAT_NUMBER | STRING | SYMBOL", ValueRetrieval, [0]),
    ("atype : NULL_TYPE | BOOL_TYPE | INTEGER_TYPE | FLOAT_TYPE | STRING_TYPE | REGISTER_TYPE",
     TypeRKW, [0])
]

# s = [("program : genexpr genexpr", Program, [0, 1]),
#      ("genexpr : datadec", GenExpr, [0]),
#      ("genexpr : ", GenExpr, []),
#      ("datadec : atype SYMBOL sizedec valueexpr", DataDeclaration, [0, 1, 2, 3]),
#      ("atype : REGISTER_TYPE", TypeRKW, [0]),
#      ("sizedec : OPEN valueret CLOSE", SizeDeclaration, [1]),
#      ("valueret : INT_NUMBER | SYMBOL", ValueRetrieval, [0]),
#      ("valueexpr : ", ValueExpr, [])
#      ]

# s = [("program : REGISTER_TYPE SYMBOL OPEN INT_NUMBER CLOSE", Test, [0, 1, 3])]
