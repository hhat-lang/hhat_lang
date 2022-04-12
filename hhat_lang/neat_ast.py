"""AST"""

from rply.token import BaseBox, Token

"""
below, some string keywords are defined
to use as reference in the right context
to build the ast.

ex:
	prefix:suffix
"""

# as prefix:
START = 'start'
END = 'end'

# as suffix:
BUILTIN = 'builtin'
OPERATOR = 'op'
ID = 'identity'
ATTR_DECL = 'attr_decl'
ATTR_ASSIGN = 'attr_assign'
TYPE_PARAMS = 'type_params'
PARAMS = 'params'
BODY = 'body'
RANGE = 'range'
INDEX_ASSIGNEE = 'index'
VALUE_ASSIGNEE = 'assign'
LOOP_ASSIGNEE = 'loop_var'
CALL = 'call'
CALLER = 'caller'
CALL_ARGS = 'call_args'
COND = 'cond'
TESTS = 'tests'
LOOP = 'loop'
LOOP_OBJ = 'loop_obj'
RESULT = 'return'


# as both
TYPE = 'type'
SYMBOL = 'symbol'


class SuperBox(BaseBox):
    def __init__(self):
        self.value = ()
        self.value_str = ""
        self.name = self.__class__.__name__

    def check_obj(self, grammar_obj):
    	if isinstance(grammar_obj, (Token, SuperBox)):
    		if grammar_obj.value:
    			return True
    	return False

    def plain_value(self, grammar_obj):
    	return grammar_obj.value

    def get_value(self, grammar_obj):
    	if isinstance(grammar_obj, SuperBox):
    		return grammar_obj.value
    	if isinstance(grammar_obj, Token):
    		split_res = grammar_obj.name.split('_')
    		if len(split_res) == 1:
    			pre = split_res[0]
    			if pre in ['SYMBOL', 'QSYMBOL']:
    				prefix = 'symbol'
    		elif len(split_res) == 2:
    			pre, post = split_res
	    		if pre in ['EQ', 'NEQ', 'GT', 'GTE', 'LT', 'LTE', 'NOT']:
	    			prefix = OPERATOR
	    		elif post in ['TYPE', 'LITERAL']:
	    			prefix = pre.lower()
	    		elif post in ['GATE', 'BUILTIN']:
	    			prefix = post.lower()
	    		else:
	    			prefix = 'unknown'
    		return (f'{prefix}:{grammar_obj.value}',)
    	raise ValueError(f"-> {grammar_obj} is not a valid object.")

    def __repr__(self):
        return f"{self.__class__.__name__}(\n  {self.value_str}\n )"


class Program(SuperBox):
	def __init__(self, funcs=None, main=None):
		super().__init__()
		if self.check_obj(funcs):
			self.value = (self.get_value(funcs),)
		if self.check_obj(main):
			self.value += (self.get_value(main),)


class Function(SuperBox):
	def __init__(self, func_type=None, func_template=None, funcs=None):
		super().__init__()
		if self.check_obj(func_type):
			_name = self.plain_value(func_type)
			self.value += (f'{START}:{_name}',)
			if _name == 'main':
				pass
			elif _name == 'func':
				self.value += (func_template.value[1][0],)
		if self.check_obj(func_template):
			self.value += (self.get_value(func_template),)
			self.value += (f'{END}:{_name}',)
		if self.check_obj(funcs):
			self.value += (self.get_value(funcs),)


class FuncTemplate(SuperBox):
	def __init__(self, a_type, a_symbol, params, body, result):
		super().__init__()
		self.value += (f'{START}:{ID}',)
		self.value += (self.get_value(a_symbol) + self.get_value(a_type),)
		self.value += (f'{END}:{ID}',) 
		if self.check_obj(params):
			self.value += (f'{START}:{PARAMS}', self.get_value(params), f'{END}:{PARAMS}',)
		if self.check_obj(body):
			self.value += (f'{START}:{BODY}', self.get_value(body), f'{END}:{BODY}',)
		if self.check_obj(result):
			self.value += (f'{START}:{RESULT}', self.get_value(result), f'{END}:{RESULT}')


class Params(SuperBox):
	def __init__(self, a_type=None, a_symbol=None, func_params=None):
		super().__init__()
		if self.check_obj(a_type) and self.check_obj(a_symbol):
			self.value += (self.get_value(a_symbol) + self.get_value(a_type),)
		if self.check_obj(func_params):
			self.value += self.get_value(func_params)

class AThing(SuperBox):
	def __init__(self, a_name, a_value):
		super().__init__()
		self.value += (f'{a_name}:{self.plain_value(a_value)}',)


class Body(SuperBox):
	def __init__(self, first_instr=None, body=None):
		super().__init__()
		if self.check_obj(first_instr):
			self.value += (self.get_value(first_instr),)
		if self.check_obj(body):
			self.value += self.get_value(body)


class AttrDecl(SuperBox):
	def __init__(self, a_type, a_symbol, a_expr=None, attr_decl_assign=None):
		super().__init__()
		self.value += (f'{START}:{ATTR_DECL}',)
		value = (f'{START}:{ID}',)
		if self.check_obj(a_expr):
			sub_value += self.get_value(a_symbol)
			sub_value = (f'{START}:{TYPE_PARAMS}',)
			sub_value += (self.get_value(a_expr),)
			sub_value += (f'{END}:{TYPE_PARAMS}',)
			sub_value += self.get_value(a_type)
			value += (sub_value,)
		else:
			value += (self.get_value(a_symbol) + self.get_value(a_type),)
		value += (f'{END}:{ID}',)
		if self.check_obj(attr_decl_assign):
			value += (f'{START}:{ATTR_ASSIGN}',)
			value += (self.get_value(attr_decl_assign),)
			value += (f'{END}:{ATTR_ASSIGN}',)
		self.value += (value,)
		self.value += (f'{END}:{ATTR_DECL}',)


class Expr(SuperBox):
	def __init__(self, val1, val2=None):
		super().__init__()
		if self.check_obj(val2):
			self.value += (f'{START}:{RANGE}',)
			self.value += (self.get_value(val1) + self.get_value(val2),)
			self.value += (f'{END}:{RANGE}',)
		else:
			self.value += self.get_value(val1)


class ManyExprs(SuperBox):
	def __init__(self, expr1=None, expr2=None):
		super().__init__()
		if self.check_obj(expr1):
			value = (self.get_value(expr1),)
			if self.check_obj(expr2):
				value += self.get_value(expr2)
			self.value += value


class Entity(SuperBox):
	def __init__(self, expr1, expr2=None):
		super().__init__()
		value_start = f'{START}:{VALUE_ASSIGNEE}'
		value_end = f'{END}:{VALUE_ASSIGNEE}'
		if self.check_obj(expr2):
			idx_start = f'{START}:{INDEX_ASSIGNEE}'
			idx_end = f'{END}:{INDEX_ASSIGNEE}'
			value = (idx_start, self.get_value(expr1), idx_end)
			self.value += value
			value_assignee = expr2
		else:
			value_assignee = expr1
		self.value += (value_start, self.get_value(value_assignee), value_end)


class AttrAssign(SuperBox):
	def __init__(self, a_symbol, func_args=None):
		super().__init__()
		self.value += (f'{START}:{ATTR_ASSIGN}',)
		self.value += self.get_value(a_symbol)
		if self.check_obj(func_args):
			self.value += (self.get_value(func_args),)
		self.value += (f'{END}:{ATTR_ASSIGN}',)


class Call(SuperBox):
	def __init__(self, caller, call_args=None):
		super().__init__()
		self.value += (f'{START}:{CALL}',)
		if self.check_obj(call_args):
			call_start = f'{START}:{CALL_ARGS}'
			call_end = f'{END}:{CALL_ARGS}'
			value = (call_start, self.get_value(call_args), call_end)
			self.value += (value,)
		self.value += self.get_value(caller)
		self.value += (f'{END}:{CALL}',)


class Func(SuperBox):
	def __init__(self, val):
		super().__init__()
		self.value += self.get_value(val)


class IfStmt(SuperBox):
	def __init__(self, tests, body, elif_stmt, else_stmt):
		super().__init__()
		self.value += (f'{START}:{COND}',)
		value = (f'{START}:{TESTS}', self.get_value(tests), f'{END}:{TESTS}')
		value += (f'{START}:{BODY}', self.get_value(body), f'{END}:{BODY}')
		if self.check_obj(elif_stmt):
			value += self.get_value(elif_stmt)
		if self.check_obj(else_stmt):
			value += (self.get_value(else_stmt),)
		self.value += value
		self.value += (f'{END}:{COND}',)


class ElifStmt(SuperBox):
	def __init__(self, tests=None, body=None, elif_stmt=None):
		super().__init__()
		if self.check_obj(tests) and self.check_obj(body):
			value = (f'{START}:{TESTS}', self.get_value(tests), f'{END}:{TESTS}')
			value += (f'{START}:{BODY}', self.get_value(body), f'{END}:{BODY}')
			self.value += (value,)
			if self.check_obj(elif_stmt):
				self.value += self.get_value(elif_stmt)


class ElseStmt(SuperBox):
	def __init__(self, body=None):
		super().__init__()
		if self.check_obj(body):
			self.value += (f'{START}:{BODY}', self.get_value(body), f'{END}:{BODY}')


class Tests(SuperBox):
	def __init__(self, logic_ops, expr, more_expr):
		super().__init__()
		self.value += (self.get_value(logic_ops),)
		self.value += (self.get_value(expr),)
		self.value += (self.get_value(more_expr),)


class ForLoop(SuperBox):
	def __init__(self, expr, entity):
		super().__init__()
		self.value = (f'{START}:{LOOP}',)
		value_obj += (f'{START}:{LOOP_OBJ}', self.get_value(expr), f'{END}:{LOOP_OBJ}')
		self.value += value_obj
		value_body = (f'{START}:{BODY}', self.get_value(entity), f'{END}:{BODY}')
		self.value += (f'{END}:{LOOP}',)


