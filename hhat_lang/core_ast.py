try:
    from hhat_lang.data_ast import (DataDeclaration, DataAssign, DataCall)
except ImportError:
    from data_ast import (DataDeclaration, DataAssign, DataCall)
from rply.token import BaseBox, Token
from typing import Union


class SuperBox(BaseBox):
    def __init__(self):
        self.value = ()
        self.value_str = ""

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value_str})"


#################
# ROOT CLASSES #
################
class TypeRKW(SuperBox):
    def __init__(self, atype: Token):
        super().__init__()
        self.value = atype
        self.value_str += str(self.value)


class ASymbol(SuperBox):
    def __init__(self, symbol: Token):
        super().__init__()
        self.value = symbol
        self.value_str += str(self.value)


class AValue(SuperBox):
    def __init__(self, value: Union[Token, ASymbol]):
        super().__init__()
        self.value = value if isinstance(value, Token) else value.value
        self.value_str += str(self.value)


class OptAssign(SuperBox):
    def __init__(self, value: Union[Token, 'ValueCallExpr2'] = None):
        super().__init__()
        if value:
            if isinstance(value, Token):
                self.value = value
            else:
                self.value = value.value
        self.value_str += str(self.value)


class ARKW(SuperBox):
    def __init__(self, value: Token):
        super().__init__()
        self.value = value
        self.value_str = str(value)


###########
# VCALLS #
##########
class SuperValue(SuperBox):
    def __init__(self, value: Union[AValue, DataCall, 'IfStmtExpr', 'LoopExpr']):
        super().__init__()
        self.value = value.value
        self.value_str += str(self.value)


class ValueCallExpr2(SuperBox):
    def __init__(self,
                 value1: SuperValue = None,
                 value2: 'ValueCallExpr2' = None):
        super().__init__()
        if value1:
            self.value += (value1.value,) if not isinstance(value1.value, tuple) else value1.value
            self.value_str += str(self.value)
        if value2:
            self.value += (value2.value,) if not isinstance(value2.value, tuple) else value2.value
            self.value_str += str(self.value)


class ExtValueAssign(SuperBox):
    def __init__(self,
                 value: 'ValueCallExpr',
                 opt: OptAssign = None,
                 extra: 'ExtValueAssign' = None):
        super().__init__()
        ext_vals = value if isinstance(value, Token) else value.value
        if opt:
            if opt.value:
                ext_vals.update({'opt_assign': opt.value})
        self.value += (ext_vals,)
        if extra:
            if extra.value:
                self.value += (extra.value,) if not isinstance(extra.value, tuple) else extra.value
        self.value_str += str(self.value)


class ValueAssign(SuperBox):
    def __init__(self, value: ExtValueAssign):
        super().__init__()
        if isinstance(value, Token):
            self.value += (value,)
        else:
            self.value += (value.value,) if not isinstance(value.value, tuple) else value.value
        self.value_str += str(self.value)


class ValueCallExpr(SuperBox):
    def __init__(self, value: Union[Token, ASymbol, DataCall, ARKW]):
        super().__init__()
        if isinstance(value, Token):
            self.value = {'call': value}
        else:
            self.value = {'call': value.value}
        self.value_str += str(value)


class GenExpr(SuperBox):
    def __init__(self,
                 expr: Union[DataDeclaration, DataAssign, DataCall] = None,
                 extra: 'GenExpr' = None):
        super().__init__()
        if expr:
            self.value += (expr.value,) if not isinstance(expr.value, tuple) else expr.value
            self.value_str += str(self.value)
        if extra:
            self.value += (extra.value,) if not isinstance(extra.value, tuple) else extra.value
            self.value_str += str(self.value)


#####################
# FUNCTION CLASSES #
####################
class FuncReturn(SuperBox):
    def __init__(self, func_return: ValueCallExpr2 = None):
        super().__init__()
        if func_return:
            self.value = func_return.value
            self.value_str += str(func_return)


class FuncBody(SuperBox):
    def __init__(self, f1: GenExpr = None):
        super().__init__()
        if f1:
            self.value = f1.value
            self.value_str += str(self.value)


class FuncParams(SuperBox):
    def __init__(self,
                 atype: TypeRKW = None,
                 symbol: ASymbol = None,
                 params: 'FuncParams' = None):
        super().__init__()
        func_vals = {}
        if atype and symbol:
            func_vals.update({'type': atype.value, 'symbol': symbol.value})
            self.value += (func_vals,)
            self.value_str += str(func_vals)
        if params:
            self.value += params.value
            self.value_str += str(params)


class FuncTempl(SuperBox):
    def __init__(self,
                 atype: TypeRKW,
                 symbol: ASymbol,
                 func_params: Union[tuple, dict, FuncParams] = None,
                 func_body: Union[tuple, dict, FuncBody] = None,
                 func_return: Union[tuple, dict, FuncReturn] = None):
        super().__init__()
        func_vals = {'type': atype.value, 'symbol': symbol.value}
        if not isinstance(func_params, tuple) and func_params is not None:
            if func_params.value:
                func_vals.update({'params': func_params.value})
        if not isinstance(func_body, tuple) and func_body is not None:
            if func_body.value:
                func_vals.update({'body': func_body.value})
        if not isinstance(func_return, tuple) and func_return is not None:
            if func_return.value:
                func_vals.update({'return': func_return.value})
        self.value = func_vals
        self.value_str += str(self.value)


class Main(SuperBox):
    def __init__(self, func: FuncTempl = None):
        super().__init__()
        if func:
            self.value += ({'main': func.value},)
            self.value_str += str(func)


class Function(SuperBox):
    def __init__(self, func: FuncTempl):
        super().__init__()
        self.value += ({'function': func.value},)
        self.value_str += str(func)


class Functions(SuperBox):
    def __init__(self,
                 function: Union[dict, tuple, Function] = None,
                 functions: 'Functions' = None):
        super().__init__()
        if not isinstance(function, (tuple, dict)) and function is not None:
            self.value += (function.value,) if not isinstance(function.value,
                                                              tuple) else function.value
        if functions:
            self.value += functions.value
        self.value_str += str(self.value)


##########
# LOOPS #
#########
class LoopRange(SuperBox):
    def __init__(self,
                 v1: Union[ValueCallExpr, ASymbol, DataCall],
                 v2: ValueCallExpr = None):
        super().__init__()
        lrange_vals = {'start': v1 if isinstance(v1, Token) else v1.value}
        if v2:
            lrange_vals.update({'end': v2 if isinstance(v2, Token) else v2.value})
        self.value = lrange_vals
        self.value_str = str(self.value)


class LoopExpr(SuperBox):
    def __init__(self,
                 loop_range: LoopRange,
                 func_body: FuncBody,
                 loop_var: ASymbol = None):
        super().__init__()
        loop_vals = {'loop': {'range': loop_range.value, 'body': func_body.value}}
        if loop_var:
            loop_vals.update(
                {'loop_var': loop_var if isinstance(loop_var, Token) else loop_var.value})
        self.value += (loop_vals,)
        self.value_str = str(self.value)


##################
# IF STATEMENTS #
#################
class ComparisonIfTest(SuperBox):
    def __init__(self, comparison: Token):
        super().__init__()
        self.value = comparison
        self.value_str += str(comparison)


class AppendIfTest(SuperBox):
    def __init__(self, logical_op: Token):
        super().__init__()
        self.value += logical_op
        self.value_str += str(self.value)


class BoolValue(SuperBox):
    def __init__(self,
                 value: Union[DataCall, AValue],
                 negative: Token = None):
        super().__init__()
        if negative:
            self.value += (negative,)
        self.value += value if isinstance(value, (Token,)) else value.value
        self.value_str += str(value)


class InsideIfTest(SuperBox):
    def __init__(self,
                 value1: BoolValue,
                 comparison: Token = None,
                 value2: BoolValue = None):
        super().__init__()
        self.value += (value1.value,)
        self.value_str += str(value1)
        if comparison:
            self.value += (comparison.value,)
        self.value_str += str(comparison)
        if value2:
            self.value += (value2.value,)
        self.value_str += str(value2)


class IfTests(SuperBox):
    def __init__(self,
                 test: 'IfTests',
                 append_test: AppendIfTest = None,
                 extra: 'IfTests' = None):
        super().__init__()
        self.value += ({'test': test.value},)
        if append_test:
            self.value += ({'logical_operator': append_test.value},)
        self.value_str += str(self.value)
        if extra:
            self.value += extra.value
        self.value_str += str(extra)


class ElseStmtExpr(SuperBox):
    def __init__(self, func_body: FuncBody = None):
        super().__init__()
        if func_body:
            self.value = func_body.value
        self.value_str += str(func_body)


class ElifStmtExpr(SuperBox):
    def __init__(self,
                 tests: IfTests = None,
                 func_body: FuncBody = None,
                 extra: 'ElifStmtExpr' = None):
        super().__init__()
        expr_vals = {}
        if tests and func_body:
            expr_vals.update({'tests': tests.value, 'body': func_body.value})
        self.value += (expr_vals,)
        if extra:
            self.value += extra
        self.value_str += str(self.value)


class IfStmtExpr(SuperBox):
    def __init__(self,
                 tests: InsideIfTest,
                 func_body: FuncBody,
                 elif_body: ElifStmtExpr = None,
                 else_body: ElseStmtExpr = None):
        super().__init__()
        expr_vals = {'if': {'tests': tests.value,
                            'body': func_body.value}}
        if elif_body:
            expr_vals.update({'elifs': elif_body})
        if else_body:
            expr_vals.update({'else': {'body': else_body}})
        self.value += (expr_vals,)
        self.value_str += str(self.value)


############
# IMPORTS #
###########
class Imports(SuperBox):
    def __init__(self, value=None):
        super().__init__()
        if value:
            self.value = {'imports': value.value}
            self.value_str = str(self.value)


class ImportSymbol(SuperBox):
    def __init__(self, s1=None, s2=None):
        super().__init__()
        if s1:
            self.value += (s1.value,)
        if s2:
            self.value += (s2.value,)


#################
# MAIN PROGRAM #
################
class Program(SuperBox):
    def __init__(self,
                 functions: Functions,
                 main: Main = None,
                 importing: Union[dict, tuple, Imports] = None):
        super().__init__()
        if not isinstance(importing, tuple) and importing is not None:
            if importing.value:
                self.value += (importing.value,)
        self.value += (functions.value,) if not isinstance(functions.value,
                                                           tuple) else functions.value
        if main:
            self.value += (main.value,) if not isinstance(main.value, tuple) else main.value
        self.value_str += str(self.value)
        self.value_str = str(self.value)
