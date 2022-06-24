"""AST"""

from rply.token import BaseBox, Token
from hhat_lang.symbolic import FST

"""
Program
Function
FuncTemplate
Params
AThing
Body
AttrDecl
Expr
ManyExprs
Entity
AttrAssign
Call
Func
IfStmt
ElifStmt
ElseStmt
Tests
ForLoop
--
Range
IndexAssign
ParamsSeq
TypeExpr
AttrHeader
Args
ExitBody
"""


class SuperBox(BaseBox):
    symbolic = FST()

    def __init__(self):
        self.value = ()
        self.local_stats = {'cur_value': '',
                            'cur_type': '',
                            'cur_params': (),
                            'cur_body': (),
                            'cur_return': ()}

    @staticmethod
    def check_token(_token):
        if isinstance(_token, (Token, SuperBox)):
            if _token.value:
                return True
        if isinstance(_token, tuple):
            if _token:
                return True
        return False

    def run_out_exprs(self, data):
        if isinstance(data, (ManyExprs, Token, Expr)):
            return self.run_out_exprs(data.value)
        if isinstance(data, tuple):
            res = ()
            for k in data:
                res += self.run_out_exprs(k)
            return res
        return data,

    def get_caller(self, data):
        if isinstance(data, tuple):
            res = ()
            for k in data:
                res += self.get_caller(k)
            return res
        if isinstance(data, Caller):
            return data,
        return self.get_caller(data.value)

    def show_code(self):
        header = ' depth code |   symbol   |  position'
        print(header)
        print('-' * (len(header) + 30))
        self.recur_tokens()

    def recur_tokens(self, code=None, depth=0):
        if code is None:
            code = self.value
        if isinstance(code, tuple):
            for k in code:
                if isinstance(k, SuperBox):
                    self.recur_tokens(k.value, depth=depth + 1)
                else:
                    self.recur_tokens(k, depth=depth + 1)
        else:
            if isinstance(code, Token):
                if code.source_pos:
                    lineno = code.source_pos.lineno
                    colno = code.source_pos.colno
                    idx = code.source_pos.idx
                    pos = f'(idx={idx}, lno={lineno}, cno={colno})'
                    str_depth = str(depth)
                    str_depth_t = ' ' * (6 - len(str_depth)) + str_depth
                    str_depth_len = '-' * (depth // 4)
                    if len(code.value) < 10:
                        str_code = ' ' * (14 - (len(code.value) + len(str_depth_len))) + code.value
                    else:
                        if len(code.value) > 12:
                            str_code = ' ' * (5 - len(str_depth_len)) + code.value[:9] + '...'
                        else:
                            str_code = ' ' * (5 - len(str_depth_len)) + code.value
                    str_pos = ' ' * (18 - (len(str_code) + len(str_depth_len))) + pos
                    print(f'{str_depth_t} {str_depth_len} {str_code} {str_pos}')


class Program(SuperBox):
    def __init__(self, funcs=None, main=None):
        super().__init__()
        if self.check_token(funcs):
            self.value += (funcs,)
        if self.check_token(main):
            self.value += (main,)


class Function(SuperBox):
    def __init__(self, func_type=None, func_template=None, funcs=None):
        super().__init__()
        if self.check_token(func_type) and self.check_token(func_template):
            self.value += (func_type, func_template,)
            _func = func_type.value
            _name = func_template.local_stats['cur_name']
            _type = func_template.local_stats['cur_type']
            _params = func_template.local_stats['cur_params']
            _body = func_template.local_stats['cur_body']
            _result = func_template.local_stats['cur_return']
            self.symbolic.create()
            self.symbolic.add(value=_type, key='type')
            self.symbolic.add(value=_params, key='params')
            self.symbolic.add(value=_body, key='body')
            self.symbolic.add(value=_result, key='return')
            self.symbolic.create(name=_name, func=_func)
            self.symbolic.move_cur_to(name=_name)
            if self.check_token(funcs):
                self.value += funcs.value


class FuncTemplate(SuperBox):
    def __init__(self, a_type, a_symbol, params, body, result):
        super().__init__()
        self.value += ((a_symbol, a_type,),)
        self.local_stats['cur_name'] = a_symbol.value.value
        self.local_stats['cur_type'] = a_type.value.value
        if self.check_token(params):
            self.value += (params,)
            self.local_stats['cur_params'] = params.value
        if self.check_token(body):
            self.value += (body,)
            self.local_stats['cur_body'] = body.value
        if self.check_token(result):
            self.value += (result,)
            self.local_stats['cur_return'] = result.value


class Params(SuperBox):
    def __init__(self, a_type=None, a_symbol=None, func_params=None, typeexpr=None):
        super().__init__()
        if self.check_token(a_type) and self.check_token(a_symbol):
            if self.check_token(typeexpr):
                self.value += (ParamsSeq(a_symbol, a_type).value,)
            else:
                self.value += (ParamsSeq(a_symbol, a_type, typeexpr).value,)
            if self.check_token(func_params):
                self.value += func_params.value


class ABuiltIn(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = AThing(value)


class AThing(SuperBox):
    def __init__(self, value):
        super().__init__()
        if isinstance(value, str):
            self.value = value
        else:
            self.value = value.value
            if isinstance(value, Token):
                _val = value
            else:
                _val = value.value
            self.name = _val.name
            self.source_pos = _val.source_pos
            self.lineno = _val.source_pos.lineno
            self.colno = _val.source_pos.colno
            self.idx = _val.source_pos.idx


class AType(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = AThing(value)


class ASymbol(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = AThing(value)


class AQSymbol(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = AThing(value)


class Body(SuperBox):
    def __init__(self, first_instr=None, others_instrs=None):
        super().__init__()
        if self.check_token(first_instr):
            self.value += (first_instr,)
            if self.check_token(others_instrs):
                self.value += others_instrs.value


class AttrDecl(SuperBox):
    def __init__(self, a_type, a_symbol, a_expr=None, attr_decl_assign=None):
        super().__init__()
        self.value = (AttrHeader(a_symbol, a_type, a_expr),)
        if self.check_token(attr_decl_assign):
            self.value += self.run_out_exprs(attr_decl_assign)


class Expr(SuperBox):
    def __init__(self, val1, val2=None):
        super().__init__()
        if self.check_token(val2):
            new_val1 = self.run_out_exprs(val1)
            new_val2 = self.run_out_exprs(val2)
            self.value = Range(new_val1, new_val2)
        else:
            self.value = self.run_out_exprs(val1)


class ManyExprs(SuperBox):
    def __init__(self, expr1=None, expr2=None, expr3=None):
        super().__init__()
        if self.check_token(expr3):
            self.value += self.run_out_exprs(expr3)
        if self.check_token(expr1):
            self.value += self.run_out_exprs(expr1)
            if self.check_token(expr2):
                self.value += self.run_out_exprs(expr2)


class Entity(SuperBox):
    def __init__(self, expr1, expr2=None):
        super().__init__()
        value = ()
        new_expr1 = self.run_out_exprs(expr1)
        if self.check_token(expr2):
            new_expr2 = self.run_out_exprs(expr2)
            value = (IndexAssign(new_expr1),)
            if new_expr2 == 'print':
                value += (Caller(new_expr2),)
            else:
                value += (ExprAssign(new_expr2),)

        else:
            if new_expr1 == 'print':
                value += (IndexAssign(), Caller(new_expr1),)
            else:
                value = (IndexAssign(), ExprAssign(new_expr1),)
        self.value += value


class AttrAssign(SuperBox):
    def __init__(self, a_symbol, func_args):
        super().__init__()
        self.value += (a_symbol, func_args,)


class Call(SuperBox):
    def __init__(self, caller, call_args=None):
        super().__init__()
        if self.check_token(call_args):
            self.value += (Args(call_args), Caller(caller))
        else:
            self.value += (Caller(caller),)


class Func(SuperBox):
    def __init__(self, val):
        super().__init__()
        self.value = (val,)


class IfStmt(SuperBox):
    def __init__(self, tests, body, elif_stmt, else_stmt):
        super().__init__()
        self.value += ((tests, body, ExitBody()),)
        if self.check_token(elif_stmt):
            self.value += (elif_stmt,)
        if self.check_token(else_stmt):
            self.value += (else_stmt,)


class ElifStmt(SuperBox):
    def __init__(self, tests=None, body=None, elif_stmt=None):
        super().__init__()
        if self.check_token(tests):
            if self.check_token(body):
                self.value += ((tests, body, ExitBody()),)
            else:
                self.value += (tests,)
            if self.check_token(elif_stmt):
                self.value += (elif_stmt,)


class ElseStmt(SuperBox):
    def __init__(self, body=None):
        super().__init__()
        if self.check_token(body):
            self.value += (body, ExitBody())


class Tests(SuperBox):
    def __init__(self, logic_ops, expr, more_expr):
        super().__init__()
        self.value = (Args(expr, more_expr), self.get_caller(logic_ops))


class ForLoop(SuperBox):
    def __init__(self, expr, entity, more_entity):
        super().__init__()
        self.value += ((expr, entity),)
        if self.check_token(more_entity):
            self.value += more_entity.value


# extra classes

class Range(SuperBox):
    def __init__(self, val1, val2=None):
        super().__init__()
        if self.check_token(val2):
            self.value = (val1, val2)
        else:
            self.value = (val1,)


class IndexAssign(SuperBox):
    def __init__(self, val=None):
        super().__init__()
        if self.check_token(val):
            self.value = self.run_out_exprs(val)
        else:
            self.value = AThing('*all*')


class ExprAssign(SuperBox):
    def __init__(self, expr):
        super().__init__()
        self.value = self.run_out_exprs(expr)


class ParamsSeq(SuperBox):
    def __init__(self, a_symbol, a_type, a_expr=None):
        super().__init__()
        if self.check_token(a_expr):
            self.value = ({'symbol': a_symbol.value, 'type': a_type.value, 'len': a_expr.value})
        else:
            self.value = ({'symbol': a_symbol.value, 'type': a_type.value})


class TypeExpr(SuperBox):
    def __init__(self, a_expr):
        super().__init__()
        self.value = self.run_out_exprs(a_expr)


class AttrHeader(SuperBox):
    def __init__(self, a_symbol, a_type, a_expr=None):
        super().__init__()
        if self.check_token(a_expr):
            self.value = (a_symbol, (TypeExpr(a_expr), Caller(a_type)))
        else:
            self.value = (a_symbol, a_type)


class Args(SuperBox):
    def __init__(self, *args):
        super().__init__()
        value = ()
        for k in args:
            value += self.run_out_exprs(k)
        self.value = (value,)


class Caller(SuperBox):
    def __init__(self, caller):
        super().__init__()
        self.value = (caller,)


class ExitBody(SuperBox):
    def __init__(self):
        super().__init__()
        self.value = 'exit_cond_body'
