"""
Tokens
"""

tokens = {}
tokens.update({"OPEN": r"\("})
tokens.update({"CLOSE": r"\)"})

tokens.update({"ASSIGN": r"=(?!=)"})
tokens.update({"COLON": r":"})
tokens.update({"STAR": r"\*"})
tokens.update({"COMMA": r"\,"})

tokens.update({"IMPORTS": r"imports(?!\w)"})
tokens.update({"MAIN": r"main(?!\w)"})
tokens.update({"FUNCTION": r"func(?!\w)"})
tokens.update({"RETURN": r"return(?!\w)"})

tokens.update({"IF_COND": r"if(?!\w)"})
tokens.update({"ELIF_COND": r"elif(?!\w)"})
tokens.update({"ELSE_COND": r"else(?!\w)"})

tokens.update({"AND_LOGOP": r"\+"})
tokens.update({"OR_LOGOP": r"\-"})
tokens.update({"NOT_LOGOP": r"not(?!\w)"})

tokens.update({"FOR_LOOP": r"for(?!\w)"})
tokens.update({"IN_LOOP": r"in(?!\w)"})
tokens.update({"RANGE_LOOP": r"\.\."})
tokens.update({"AS": r"as(?!\w)"})

tokens.update({"EQ_SIGN": r"=="})
tokens.update({"GT_SIGN": r">"})
tokens.update({"LT_SIGN": r"<"})
tokens.update({"GET_SIGN": r">="})
tokens.update({"LET_SIGN": r"<="})
tokens.update({"NEQ_SIGN": r"!="})

tokens.update({"NULL_TYPE": r"null(?!\w)"})
tokens.update({"INTEGER_TYPE": r"int(?!\w)"})
tokens.update({"FLOAT_TYPE": r"float(?!\w)"})
tokens.update({"BOOL_TYPE": r"bool(?!\w)"})
tokens.update({"STR_TYPE": r"str(?!\w)"})
tokens.update({"GATES_TYPE": r"circuit(?!\w)"})
tokens.update({"REGISTER_TYPE": r"register(?!\w)"})
tokens.update({"LIST_TYPE": r"list(?!\w)"})
tokens.update({"HASHMAP_TYPE": r"hashmap(?!\w)"})
tokens.update({"MEAS_TYPE": r"measurement(?!\w)"})

tokens.update({"TRUE_LITERAL": r"T(?!\w)"})
tokens.update({"FALSE_LITERAL": r"F(?!\w)"})

tokens.update({"H_GATE": r"@h(?!\w)"})
tokens.update({"X_GATE": r"@x(?!\w)"})
tokens.update({"Z_GATE": r"@z(?!\w)"})
tokens.update({"Y_GATE": r"@y(?!\w)"})
tokens.update({"CNOT_GATE": r"@cnot(?!\w)"})
tokens.update({"SWAP_GATE": r"@swap(?!\w)"})
tokens.update({"CZ_GATE": r"@cz(?!\w)"})
tokens.update({"RX_GATE": r"@rx(?!\w)"})
tokens.update({"RZ_GATE": r"@rz(?!\w)"})
tokens.update({"RY_GATE": r"@ry(?!\w)"})
tokens.update({"T_GATE": r"@t(?!\w)"})
tokens.update({"T_DAG_GATE": r"@tdag(?!\w)"})
tokens.update({"S_GATE": r"@s(?!\w)"})
tokens.update({"S_DAG_GATE": r"@sdag(?!\w)"})
tokens.update({"CR_GATE": r"@cr(?!\w)"})
tokens.update({"TOFFOLI_GATE": r"@toffoli(?!\w)"})

tokens.update({"SUPERPOSN_GATE": r"@superposn(?!\w)"})
tokens.update({"AMPLIFICATION_GATE": r"@ampl(?!\w)"})

tokens.update({"RESET_GATE": r"@reset(?!\w)"})
tokens.update({"MEASURE_BUILTIN": r"@return(?!\w)"})

tokens.update({"ADD_BUILTIN": r"add(?!\w)"})
tokens.update({"SUB_BUILTIN": r"sub(?!\w)"})
tokens.update({"MULT_BUILTIN": r"mult(?!\w)"})
tokens.update({"DIV_BUILTIN": r"div(?!\w)"})
tokens.update({"POWER_BUILTIN": r"power(?!\w)"})
tokens.update({"SQRT_BUILTIN": r"sqrt(?!\w)"})
tokens.update({"INT_SQRT_BUILTIN": r"int_sqrt(?!\w)"})
tokens.update({"LEN_BUILTIN": r"len(?!\w)"})
tokens.update({"SIZE_BUILTIN": r"size(?!\w)"})

tokens.update({"PRINT_BUILTIN": r"print(?!\w)"})
tokens.update({"OUTPUT_BUILTIN": r"output(?!\w)"})
tokens.update({"INPUT_BUILTIN": r"input(?!\w)"})

tokens.update({"SYMBOL": r"[a-zA-Z_]+[a-zA-Z_0-9]*"})
tokens.update({"QSYMBOL": r"@[a-zA-Z_]+[a-zA-Z_0-9]*"})

tokens.update({"INT_LITERAL": r"[-+]?[0-9]+"})
tokens.update({"FLOAT_LITERAL": r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"})
# tokens.update({"IMAG_LITERAL": r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?j(?!\w)"})
tokens.update({"STR_LITERAL": r"(\'(.+?)\'|\"(.+?)\")"})


# * insert new tokens below *
