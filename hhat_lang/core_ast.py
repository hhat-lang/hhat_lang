"""Core AST"""

from rply.token import BaseBox, Token

# PREFIX
SCOPE = 'scope'
MAIN = 'main'
CODE = 'code'
PARAMS = 'params'
BODY = 'body'
SYMBOL = 'symbol'
QSYMBOL = 'qsymbol'
TYPE = 'type'
INDICES = 'indices'
BUILTIN = 'builtin'
LOOP = 'loop'
END = 'end'

# SUFFIX
ATTR_DECL = 'attr_decl'
SIZE_DECL = 'size_decl'
ASSIGN_EXPR = 'assign_expr'
ASSIGN_VALUE = 'assign_value'
OPT_ASSIGN = 'opt_assign'
NO_OPT = 'all'
OPT_STAR = 'self'
CALL = 'call'
CALLER = 'caller'
CALLER_ARGS = 'caller_args'
ATTR_ASSIGN = 'attr_assign'
LOOP_START = 'loop_start'
LOOP_END = 'loop_end'


class SuperBox(BaseBox):
    def __init__(self):
        self.value = ()
        self.value_str = ""
        self.name = self.__class__.__name__

    @staticmethod
    def check_grammar_obj(grammar_obj):
        if grammar_obj is None:
            return False
        if grammar_obj.value:
            return True
        return False

    def get_value(self, grammar_obj):
        if isinstance(grammar_obj, Token):
            g_name = grammar_obj.name.split('_')[-1]
            if g_name in ['BUILTIN', 'GATE']:
                _prefix = g_name.lower()
            elif g_name in ['LITERAL']:
                _prefix = grammar_obj.name.split('_')[0].lower()
            elif g_name in ['SYMBOL']:
                return self.get_right_symbol(grammar_obj)
            else:
                _prefix = grammar_obj.name.lower()
            return f'{_prefix}:{grammar_obj.value}'
        return grammar_obj.value

    @staticmethod
    def get_right_symbol(symbol):
        if isinstance(symbol, Token):
            _sym_name = symbol.name
            _sym_val = symbol.value
        else:
            _sym_name = symbol.value.name
            _sym_val = symbol.value.value
        if _sym_name == 'QSYMBOL':
            return f'{QSYMBOL}:{_sym_val}'
        if _sym_name == 'SYMBOL':
            return f'{SYMBOL}:{_sym_val}'
        return ''

    def get_grammar_obj(self, grammar_obj, prefix=CODE, suffix=None):
        if suffix:
            if self.check_grammar_obj(grammar_obj):
                _code = f'{prefix}:{suffix}'
                _end = f'{END}:{suffix}'
                return _code, grammar_obj.value, _end
            return ()
        raise AttributeError("Suffix object must not be None.")

    def set_str_code(self, grammar_obj, prefix=None):
        if grammar_obj:
            if prefix is None or prefix in ['QSYMBOL', 'SYMBOL']:
                res = self.get_right_symbol(grammar_obj)
                if res:
                    return res
                raise AttributeError("prefix object must not be None.")
            return f'{prefix}:{grammar_obj.value.value}'
        return ''

    def build_value_str(self, *args):
        _val = ''
        for k in args:
            if isinstance(k, Token):
                _val += f'{k}=('
                _val += f'line: {k.source_pos.lineno}, col: {k.source_pos.colno})\n'
            else:
                _val += f'{k}\n'
        self.value_str += _val

    def __repr__(self):
        return f"{self.__class__.__name__}(\n  {self.value_str}\n )"


class Main(SuperBox):
    def __init__(self, any_type, any_symbol, func_params=None, body_exprs=None):
        super().__init__()
        _code_main = f'{SCOPE}:{MAIN}'
        _end_main = f'{END}:{MAIN}'
        _type = f'{TYPE}:{any_type.value.value}'
        _symbol = self.get_value(any_symbol)  # self.get_right_symbol(any_symbol)
        self.value += (_code_main, _symbol, _type)
        self.value += self.get_grammar_obj(func_params, CODE, PARAMS)
        self.value += self.get_grammar_obj(body_exprs, CODE, BODY)
        self.value += (_end_main,)


class AnyType(SuperBox):
    def __init__(self, any_type: Token):
        super().__init__()
        self.value = any_type


class AnySymbol(SuperBox):
    def __init__(self, any_symbol: Token):
        super().__init__()
        self.value = self.get_right_symbol(any_symbol)


class FuncParams(SuperBox):
    def __init__(self, any_type=None, any_symbol=None, func_args=None):
        super().__init__()
        _type = self.set_str_code(any_type, TYPE)
        _symbol = self.get_value(any_symbol) # self.set_str_code(any_symbol, SYMBOL)
        if self.check_grammar_obj(any_type) and self.check_grammar_obj(any_symbol):
            self.value += ((_symbol, _type,),)
        if self.check_grammar_obj(func_args):
            self.value += self.get_value(func_args)


class Empty(SuperBox):
    def __init__(self):
        super().__init__()
        self.value = ()


class BodyExprs(SuperBox):
    def __init__(self, first_expr, other_exprs):
        super().__init__()
        self.value += (self.get_value(first_expr),)
        if self.check_grammar_obj(other_exprs):
            self.value += self.get_value(other_exprs)


class AttrDecl(SuperBox):
    def __init__(self, any_type, any_symbol, size_decl, assign_exprs):
        super().__init__()
        _start0 = f'{CODE}:{ATTR_DECL}'
        _end0 = f'{END}:{ATTR_DECL}'
        _type = f'{TYPE}:{any_type.value.value}'
        _symbol = self.get_value(any_symbol)
        self.value += (_start0, _symbol, _type)
        if self.check_grammar_obj(size_decl):
            _start = f'{CODE}:{SIZE_DECL}'
            _end = f'{END}:{SIZE_DECL}'
            self.value += (_start, self.get_value(size_decl), _end)
        self.value += (_end0,)
        if self.check_grammar_obj(assign_exprs):
            _start = f'{CODE}:{ASSIGN_EXPR}'
            _end = f'{END}:{ASSIGN_EXPR}'
            self.value += (_start, self.get_value(assign_exprs), _end)


class GenericExprs1(SuperBox):
    def __init__(self, param1):
        super().__init__()
        self.value = self.get_value(param1)


class AssignValues(SuperBox):
    def __init__(self, opt_assign, any_call, assign_values):
        super().__init__()
        _start = f'{CODE}:{ASSIGN_VALUE}'
        _end = f'{END}:{ASSIGN_VALUE}'
        _opt = self.get_value(opt_assign)
        _assignee = self.get_value(any_call)
        self.value = ((_opt, _start, _assignee, _end),)
        if self.check_grammar_obj(assign_values):
            self.value += self.get_value(assign_values)


class OptAssign(SuperBox):
    def __init__(self, opt_value=None):
        super().__init__()
        _val = f'{CODE}:{OPT_ASSIGN}'
        if self.check_grammar_obj(opt_value):
            if isinstance(opt_value, Token):
                if opt_value.name == 'STAR':
                    _val2 = f'{INDICES}:{OPT_STAR}'
                else:
                    _val2 = self.get_value(opt_value)
            else:
                _val2 = self.get_value(opt_value)
        else:
            _val2 = f'{INDICES}:{NO_OPT}'
        _val3 = f'{END}:{OPT_ASSIGN}'
        self.value = (_val, _val2, _val3)


class AnyCall(SuperBox):
    def __init__(self, param1, param2=None):
        super().__init__()
        if param1.name != self.name:
            _start = f'{CODE}:{CALL}'
            _end = f'{END}:{CALL}'
            self.value = (_start, self.get_value(param1), _end)
            if self.check_grammar_obj(param2):
                self.value += self.get_value(param2)
        else:
            self.value = self.get_value(param1)
            if self.check_grammar_obj(param2):
                self.value += self.get_value(param2)


class InsideCall(SuperBox):
    def __init__(self, param1, param2=None):
        super().__init__()
        if self.check_grammar_obj(param2):
            _start2 = f'{CODE}:{CALLER_ARGS}'
            _end2 = f'{END}:{CALLER_ARGS}'
            self.value = (_start2, self.get_value(param2), _end2)
        if param1.name != self.name:
            _start1 = f'{CODE}:{CALLER}'
            _end1 = f'{END}:{CALLER}'
            self.value += (_start1, self.get_value(param1), _end1)
        else:
            self.value += self.get_value(param1)


class AttrAssign(SuperBox):
    def __init__(self, any_symbol, assign_values):
        super().__init__()
        _start = f'{CODE}:{ATTR_ASSIGN}'
        _end = f'{END}:{ATTR_ASSIGN}'
        _symbol = self.get_value(any_symbol)
        self.value = (_start, _symbol, _end)
        _start = f'{CODE}:{ASSIGN_EXPR}'
        _end = f'{END}:{ASSIGN_EXPR}'
        self.value += (_start, self.get_value(assign_values), _end)


class ShortLoopExprs(SuperBox):
    def __init__(self, start, end):
        super().__init__()
        _start = f'{CODE}:{LOOP}'
        _end = f'{END}:{LOOP}'
        _startl = f'{LOOP}:{LOOP_START}'
        _endl = f'{LOOP}:{LOOP_END}'
        self.value = (_start, (_startl,
                               self.get_value(start),
                               _endl,
                               self.get_value(end)),
                      _end)
