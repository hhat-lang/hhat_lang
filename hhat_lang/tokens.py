"""
Tokens
"""

tokens = {}
tokens.update({"OPEN": r"\("})
tokens.update({"CLOSE": r"\)"})

tokens.update({"ASSIGN": r"=(?!=)"})
tokens.update({"COLON": r":"})
tokens.update({"COMMA": r"\,"})

# tokens.update({"IMPORTS": r"imports(?!\w)"})
tokens.update({"MAIN": r"main(?!\w)"})
tokens.update({"FUNCTION": r"func(?!\w)"})
tokens.update({"RETURN": r"return(?!\w)"})

tokens.update({"IF_COND": r"if(?!\w)"})
tokens.update({"ELIF_COND": r"elif(?!\w)"})
tokens.update({"ELSE_COND": r"else(?!\w)"})

tokens.update({"AND_LOGOP": r"and(?!\w)"})
tokens.update({"OR_LOGOP": r"or(?!\w)"})
tokens.update({"NOT_LOGOP": r"not(?!\w)"})

tokens.update({"FOR_LOOP": r"for(?!\w)"})
tokens.update({"RANGE_LOOP": r"\.\."})

tokens.update({"EQ_OP": r"eq(?!\w)"})
tokens.update({"GT_OP": r"gt(?!\w)"})
tokens.update({"LT_OP": r"lt(?!\w)"})
tokens.update({"GTE_OP": r"gte(?!\w)"})
tokens.update({"LTE_OP": r"lte(?!\w)"})
tokens.update({"NEQ_OP": r"neq(?!\w)"})

tokens.update({"NULL_TYPE": r"null(?!\w)"})
tokens.update({"INT_TYPE": r"int(?!\w)"})
tokens.update({"FLOAT_TYPE": r"float(?!\w)"})
tokens.update({"BOOL_TYPE": r"bool(?!\w)"})
tokens.update({"STR_TYPE": r"str(?!\w)"})
tokens.update({"CIRCUIT_TYPE": r"circuit(?!\w)"})
tokens.update({"HASHMAP_TYPE": r"hashmap(?!\w)"})
tokens.update({"MEASUREMENT_TYPE": r"measurement(?!\w)"})

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
tokens.update({"T-DAG_GATE": r"@tdag(?!\w)"})
tokens.update({"S_GATE": r"@s(?!\w)"})
tokens.update({"S-DAG_GATE": r"@sdag(?!\w)"})
tokens.update({"CR_GATE": r"@cr(?!\w)"})
tokens.update({"TOFFOLI_GATE": r"@toffoli(?!\w)"})

tokens.update({"INIT_GATE": r"@init(?!\w)"})
tokens.update({"SUPERPOSN_GATE": r"@superposn(?!\w)"})
tokens.update({"AMPLIFICATION_GATE": r"@ampl(?!\w)"})
tokens.update({"SYNC_GATE": r"@sync(?!\w)"})
tokens.update({"AND_GATE": r"@and(?!\w)"})
tokens.update({"OR_GATE": r"@or(?!\w)"})
tokens.update({"RESET_GATE": r"@reset(?!\w)"})

tokens.update({"ADD_BUILTIN": r"add(?!\w)"})
tokens.update({"SUB_BUILTIN": r"sub(?!\w)"})
tokens.update({"MULT_BUILTIN": r"mult(?!\w)"})
tokens.update({"DIV_BUILTIN": r"div(?!\w)"})
tokens.update({"POWER_BUILTIN": r"power(?!\w)"})
tokens.update({"SQRT_BUILTIN": r"sqrt(?!\w)"})

tokens.update({"PRINT_BUILTIN": r"print(?!\w)"})
tokens.update({"OUTPUT_BUILTIN": r"output(?!\w)"})
tokens.update({"INPUT_BUILTIN": r"input(?!\w)"})

tokens.update({"SYMBOL": r"[a-zA-Z_]+[a-zA-Z_\-0-9]*"})
tokens.update({"QSYMBOL": r"@[a-zA-Z_]+[a-zA-Z_\-0-9]*"})

tokens.update({"INT_LITERAL": r"[-+]?[0-9]+"})
tokens.update({"FLOAT_LITERAL": r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"})
tokens.update({"STR_LITERAL": r"(\'(.+?)\'|\"(.+?)\")"})


# * insert new tokens below *
