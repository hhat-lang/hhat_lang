from rply.token import BaseBox, Token
from hht_lang.hht_datadec import (Data, DataDeclaration, DataAssign, DataCall)


class SuperBox(BaseBox):
    def __init__(self):
        self.value = ()
        self.value_str = ""

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value_str})"


class Program(SuperBox):
    def __init__(self, f1, f2=None):
        print('program!')
        super().__init__()
        self.value += (f1.value,)
        self.value_str += str(f1)
        if f2:
            self.value += (f2.value,)
            self.value_str += str(f2)


class Functions(SuperBox):
    def __init__(self, function=None, functions=None):
        super().__init__()
        if function:
            self.value += (function.value,)
            self.value_str += str(function)
        if functions:
            self.value += functions.value
            self.value_str += str(functions)


#####################
# FUNCTION CLASSES #
####################
class Function(SuperBox):
    def __init__(self, func):
        super().__init__()
        self.value += ({'function': func.value},)
        self.value_str += str(func)


class Main(SuperBox):
    def __init__(self, func=None):
        super().__init__()
        if func:
            self.value += ({'main': func.value},)
            self.value_str += str(func)


class FuncTempl(SuperBox):
    def __init__(self, atype, symbol, func_params=None, func_body=None, func_return=None):
        super().__init__()
        func_vals = {'type': atype.value, 'symbol': symbol.value}
        if func_params:
            func_vals.update({'params': func_params.value})
        if func_body:
            func_vals.update({'body': func_body.value})
        if func_return:
            func_vals.update({'return': func_return.value})
        self.value += (func_vals,)
        self.value_str += str(self.value)


class FuncParams(SuperBox):
    def __init__(self, atype=None, symbol=None, params=None):
        super().__init__()
        func_vals = {}
        if atype and symbol:
            func_vals.update({'type': atype.value, 'symbol': symbol.value})
            self.value += (func_vals,)
            self.value_str += str(func_vals)
        if params:
            self.value += params.value
            self.value_str += str(params)


class FuncBody(SuperBox):
    def __init__(self, f1=None, f2=None):
        print(f'funcbody? ({f1}, {f2})')
        super().__init__()
        if f1:
            self.value += (f1.value,)
            self.value_str += str(f1)
        if f2:
            self.value += (f2.value,)
            self.value_str += str(f2)


class FuncReturn(SuperBox):
    def __init__(self, func_return=None):
        print(f'return? {func_return}')
        super().__init__()
        if func_return:
            self.value += (func_return.value,)
            self.value_str += str(func_return)


class GenExpr(SuperBox):
    def __init__(self, expr=None, extra=None):
        print(f'genexpr? {expr}')
        super().__init__()
        if expr:
            self.value += (expr.value,) if not isinstance(expr.value, tuple) else expr.value
            self.value_str += str(expr)
        if extra:
            self.value += (extra.value,) if not isinstance(extra.value, tuple) else extra.value
            self.value_str += str(extra)


###########
# VCALLS #
##########
class ValueCallExpr(SuperBox):
    def __init__(self, value):
        print(f'valuecallexpr? {value}')
        super().__init__()
        if isinstance(value, (Token,)):
            self.value += (value,)
        else:
            self.value += (value.value,)
        self.value_str += str(value)


class ValueAssign(SuperBox):
    def __init__(self, value):
        print(f'valueassign? {value}')
        super().__init__()
        if isinstance(value, (Token,)):
            self.value += ({'assign': value},)
        else:
            self.value += ({'assign': value.value},)
        self.value_str += str(value)


class ExtValueAssign(SuperBox):
    def __init__(self, value, opt=None, extra=None):
        print(f'extvalueassign? ({value}, {opt}, {extra})')
        super().__init__()
        ext_vals = {}
        ext_vals.update({'value': value if isinstance(value, (Token,)) else value.value})
        if opt:
            ext_vals.update({'opt_assign': opt})
        self.value += (ext_vals,)
        if extra:
            self.value += extra.value
        self.value_str += str(self.value)


class ValueCallExpr2(SuperBox):
    def __init__(self, value1=None, value2=None):
        print(f'valuecallexpr2? ({value1}, {value2})')
        super().__init__()
        if value1:
            self.value += (value1.value,)
            self.value_str += str(value1)
        if value2:
            self.value += (value2.value,)
            self.value_str += str(value2)


class SuperValue(SuperBox):
    def __init__(self, value):
        print(f'supervalue? {value}')
        super().__init__()
        self.value += (value.value,)
        self.value_str += str(value)


##################
# IF STATEMENTS #
#################
class IfStmtExpr(SuperBox):
    def __init__(self, tests, func_body, elif_body=None, else_body=None):
        super().__init__()
        expr_vals = {'if': {'tests': tests.value,
                            'body': func_body.value}}
        if elif_body:
            expr_vals.update({'elifs': elif_body})
        if else_body:
            expr_vals.update({'else': {'body': else_body}})
        self.value += (expr_vals,)
        self.value_str += str(self.value)


class ElifStmtExpr(SuperBox):
    def __init__(self, tests=None, func_body=None, extra=None):
        super().__init__()
        expr_vals = {}
        if tests:
            expr_vals.update({'tests': tests.value})
        if func_body:
            expr_vals.update({'body': func_body.value})
        self.value += (expr_vals,)
        if extra:
            self.value += extra
        self.value_str += str(self.value)


class ElseStmtExpr(SuperBox):
    def __init__(self, func_body=None):
        super().__init__()
        if func_body:
            self.value = func_body.value
            self.value_str += str(func_body)


class IfTests(SuperBox):
    def __init__(self, test, append_test=None, extra=None):
        super().__init__()
        self.value += ({'test': test.value},)
        if append_test:
            self.value += ({'logical_operator': append_test.value},)
        self.value_str += str(self.value)
        if extra:
            self.value += extra.value
            self.value_str += str(extra)


class InsideIfTest(SuperBox):
    def __init__(self, value1, comparison=None, value2=None):
        super().__init__()
        self.value += (value1.value,)
        self.value_str += str(value1)
        if comparison:
            self.value += (comparison.value,)
            self.value_str += str(comparison)
        if value2:
            self.value += (value2.value,)
            self.value_str += str(value2)


class BoolValue(SuperBox):
    def __init__(self, value, negative=None):
        super().__init__()
        if negative:
            self.value += (negative,)
        self.value += value if isinstance(value, (Token,)) else value.value
        self.value_str += str(value)


class AppendIfTest(SuperBox):
    def __init__(self, logical_op):
        super().__init__()
        self.value += logical_op
        self.value_str += str(self.value)


class ComparisonIfTest(SuperBox):
    def __init__(self, comparison):
        super().__init__()
        self.value = comparison
        self.value_str += str(comparison)


##########
# LOOPS #
#########
class LoopExpr(SuperBox):
    def __init__(self, loop_range, func_body, loop_var=None):
        print(f'loopexpr? (loop_var={loop_var}, loop_range={loop_range}, func_body={func_body})')
        super().__init__()
        loop_vals = {'range': loop_range.value, 'body': func_body.value}
        if loop_var:
            loop_vals.update({'loop_var': loop_var if isinstance(loop_var, Token) else loop_var.value})
        self.value += (loop_vals,)
        self.value_str = str(self.value)


class LoopRange(SuperBox):
    def __init__(self, v1, v2=None):
        print(f'looprange? (v1={v1} v2={v2})')
        super().__init__()
        lrange_vals = {'start': v1 if isinstance(v1, Token) else v1.value}
        if v2:
            lrange_vals.update({'end': v2 if isinstance(v2, Token) else v2.value})
        self.value += (lrange_vals,)
        self.value_str = str(self.value)



#################
# ROOT CLASSES #
################
class TypeRKW(SuperBox):
    def __init__(self, atype):
        print(f'typerkw? {atype}')
        super().__init__()
        self.value = atype
        self.value_str += str(self.value)


class ASymbol(SuperBox):
    def __init__(self, symbol):
        print(f'asymbol? {symbol}')
        super().__init__()
        self.value = symbol
        self.value_str += str(self.value)


class AValue(SuperBox):
    def __init__(self, value):
        print(f'avalue? {value}')
        super().__init__()
        self.value = value
        self.value_str += str(value)


class OptAssign(SuperBox):
    def __init__(self, value=None):
        print(f'optassign? {value}')
        super().__init__()
        if value:
            if isinstance(value, Token):
                self.value += (value,)
            else:
                self.value += (value.value,)
        self.value_str += str(value)


class ARKW(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.value_str = str(value)
