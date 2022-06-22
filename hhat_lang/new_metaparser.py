"""
Metaparser
"""

import ast

try:
    from new_ast import *
except ImportError:
    from hhat_lang.new_ast import *

GRAMMAR_FILE = "grammar.txt"
PARSER_FILE = "parser.py"

grammar_dict = {'Program': Program,
                'Function': Function,
                'FuncTemplate': FuncTemplate,
                'Params': Params,
                'AThing': AThing,
                'Body': Body,
                'AttrDecl': AttrDecl,
                'Expr': Expr,
                'ManyExprs': ManyExprs,
                'Entity': Entity,
                'AttrAssign': AttrAssign,
                'Call': Call,
                'Func': Func,
                'IfStmt': IfStmt,
                'ElifStmt': ElifStmt,
                'ElseStmt': ElseStmt,
                'Tests': Tests,
                'ForLoop': ForLoop,
                'AType': AType,
                'ASymbol': ASymbol,
                'AQSymbol': AQSymbol,
                'ABuiltIn': ABuiltIn}


def get_value(word):
    if word == 'None':
        return None
    if word in ['type', 'symbol', 'builtin', 'op']:
        return f"'{word}'"
    return ast.literal_eval(word)


def get_p(word):
    if word in ['type', 'symbol', 'builtin', 'op']:
        return f"'{word}'"
    if word is None:
        return f'{word}'
    return f'p[{word}]'


def read_grammar(grammar_file=GRAMMAR_FILE):
    grammar_prod = ()
    grammar_call = ()
    grammar_args = ()
    with open(grammar_file, "r") as file:
        _res = file.read().splitlines()
    for k in _res:
        line = k.split(';')
        grammar_prod += (line[0],)
        grammar_call += (grammar_dict[line[1].replace(' ', '')],)
        _args = line[2].replace('[', '').replace(']', '').replace(' ', '')
        args_list = [get_value(p) for p in _args.split(',') if len(p) > 0]
        grammar_args += (args_list,)
    return grammar_prod, grammar_call, grammar_args


def meta_prod(values):
    val_list = values.split(" ")
    head = val_list[:2]
    val_len = len(val_list[2:])
    prod_vals = []
    for x0, x in enumerate(val_list[2:]):
        if x != '|':
            head.append(x)
        else:
            prod_vals.append('@pg.production(\"' + ' '.join(head) + '\")')
            head = val_list[:2]
        if x0 == val_len - 1:
            prod_vals.append('@pg.production(\"' + ' '.join(head) + '\")')
    return '\n'.join(prod_vals)


def create_parser_file(data):
    _meta_script = ""
    _import_list1 = ""
    _import_list2 = ""
    _import_list_all = []
    k2 = 0
    for k0, k in enumerate(data):
        words_list = ', '.join([get_p(x) for x in k[2]])
        if k[1].__name__ not in _import_list_all: # _import_list1:
            if k2 % 4 == 0 and k2 != 0:
                _import_list1 += '\n' + ' '*26
                _import_list2 += '\n' + ' '*36
            elif k2 != 0:
                _import_list1 += ' '
                _import_list2 += ' '
            k2 += 1
            _import_list1 += f'{k[1].__name__},'
            _import_list2 += f'{k[1].__name__},'
            _import_list_all.append(k[1].__name__)
        _meta_script += f"""
{meta_prod(k[0])}
def function_{k0}(p):
    return {k[1].__name__}({words_list})\n
"""
    _meta_script += """\nparser = pg.build()\n"""
    _meta_script0 = f"""
try:
    from new_ast import ({_import_list1})
    from tokens import tokens
except ImportError:
    from hhat_lang.new_ast import ({_import_list2})
    from hhat_lang.tokens import tokens
from rply import ParserGenerator
\n
pg = ParserGenerator(list(tokens.keys()))\n
"""
    _meta_script0 += _meta_script
    return _meta_script0


def save_parser(data, parser_file=PARSER_FILE):
    if parser_file[-3:] == '.py':
        with open(parser_file, "w") as file:
            file.write(data)
    else:
        raise ValueError("Wrong file type (not .py) to save the parser.")


def create_parser():
    grammar = read_grammar()
    meta_script = create_parser_file(zip(*grammar))
    save_parser(meta_script)


if __name__ == '__main__':
    create_parser()
