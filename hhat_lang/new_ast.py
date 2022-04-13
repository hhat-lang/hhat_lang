"""AST"""


from rply.token import BaseBox, Token

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
"""

class SuperBox(BaseBox):
	def __init__(self):
		self.value = ()

	@staticmethod
	def check_token(_token):
		if isinstance(_token, (Token, SuperBox)):
			if _token.value:
				return True
		if isinstance(_token, tuple):
			if _token:
				return True
		return False

	def show_code(self):
		header = ' depth code |   symbol   |  position'
		print(header)
		print('-'*(len(header)+30))
		self.recur_tokens()

	def recur_tokens(self, code=None, depth=0):
		if code is None:
			code = self.value
		if isinstance(code, tuple):
			for k in code:
				if not isinstance(k, (tuple, str, Token)):
					self.recur_tokens(k.value, depth=depth)
				else:
					self.recur_tokens(k, depth=depth+1)
		else:
			if isinstance(code, Token):
				lineno = code.source_pos.lineno
				colno = code.source_pos.colno
				idx = code.source_pos.idx
				pos = f'(idx={idx}, lno={lineno}, cno={colno})'
				str_depth = str(depth)
				str_depth_t = ' '*(6 - len(str_depth)) + str_depth
				str_depth_len = '-'*(depth//2)
				if len(code.value) < 10:
					str_code = ' '*(14 - (len(code.value) + len(str_depth_len))) + code.value
				else:
					if len(code.value) > 12:
						str_code = ' '*(5-len(str_depth_len)) + code.value[:9] + '...'
					else:
						str_code = ' '*(5-len(str_depth_len)) + code.value
				str_pos = ' '*(18 - (len(str_code)+len(str_depth_len))) + pos
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
			self.value += (func_type, (func_template,),)
			if self.check_token(funcs):
				self.value += (funcs,)


class FuncTemplate(SuperBox):
	def __init__(self, a_type, a_symbol, params, body, result):
		super().__init__()
		self.value += ((a_symbol, a_type,),)
		if self.check_token(params):
			self.value += params
		if self.check_token(body):
			self.value += (body,)
		if self.check_token(result):
			self.value += (result,)


class Params(SuperBox):
	def __init__(self, a_type=None, a_symbol=None, func_params=None):
		super().__init__()
		if self.check_token(a_type) and self.check_token(a_symbol):
			self.value += ((a_symbol, a_type,),)
			if self.check_token(func_params):
				self.value += (func_params,)


class AThing(SuperBox):
	def __init__(self, value):
		super().__init__()
		self.value = (value,)


class Body(SuperBox):
	def __init__(self, first_instr=None, others_instrs=None):
		super().__init__()
		if self.check_token(first_instr):
			self.value += ((first_instr,),)
			if self.check_token(others_instrs):
				self.value += (others_instrs,)


class AttrDecl(SuperBox):
	def __init__(self, a_type, a_symbol, a_expr=None, attr_decl_assign=None):
		super().__init__()
		if self.check_token(a_expr):
			self.value += ((a_symbol, (a_expr,), a_type,),)
		else:
			self.value += ((a_symbol, a_type,),)
		if self.check_token(attr_decl_assign):
			self.value += (attr_decl_assign,)


class Expr(SuperBox):
	def __init__(self, val1, val2=None):
		super().__init__()
		if self.check_token(val2):
			_new_token1 = (Token("Range", "range"), (val1, val2))
			self.value += _new_token1
		else:
			self.value += (val1,)


class ManyExprs(SuperBox):
	def __init__(self, expr1=None, expr2=None):
		super().__init__()
		if self.check_token(expr1):
			self.value += (expr1,)
			if self.check_token(expr2):
				self.value += (expr2,)


class Entity(SuperBox):
	def __init__(self, expr1, expr2=None):
		super().__init__()
		value = ((expr1,),)
		if self.check_token(expr2):
			value += (expr2,)
		self.value += ((value,),)


class AttrAssign(SuperBox):
	def __init__(self, a_symbol, func_args):
		super().__init__()
		self.value += (a_symbol, (func_args,),)


class Call(SuperBox):
	def __init__(self, caller, call_args=None):
		super().__init__()
		if self.check_token(call_args):
			self.value += ((call_args,), caller)
		else:
			self.value += (caller,)


class Func(SuperBox):
	def __init__(self, val):
		super().__init__()
		self.value += (val,)


class IfStmt(SuperBox):
	def __init__(self, tests, body, elif_stmt, else_stmt):
		super().__init__()
		self.value += ((tests, body,),)
		if self.check_token(elif_stmt):
			self.value += (elif_stmt,)
		if self.check_token(else_stmt):
			self.value += (else_stmt,)


class ElifStmt(SuperBox):
	def __init__(self, tests=None, body=None, elif_stmt=None):
		super().__init__()
		if self.check_token(tests):
			if self.check_token(body):
				self.value += ((tests, body),)
			else:
				self.value += (tests,)
			if self.check_token(elif_stmt):
				self.value += (elif_stmt,)


class ElseStmt(SuperBox):
	def __init__(self, body=None):
		super().__init__()
		if self.check_token(body):
			self.value += (body,)


class Tests(SuperBox):
	def __init__(self, logic_ops, expr, more_expr):
		super().__init__()
		self.value += ((logic_ops, expr,), more_expr)


class ForLoop(SuperBox):
	def __init__(self, expr, entity):
		super().__init__()
		self.value += ((expr, entity),)

