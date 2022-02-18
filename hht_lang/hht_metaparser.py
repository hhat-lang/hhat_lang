from hht_semantics import s

meta_script = f"""from hht_lang.hht_core_ast import *
from rply import ParserGenerator
from hht_lang.hht_tokens import tokens
\n
pg = ParserGenerator(list(tokens.keys()))\n
"""


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


for k0, k in enumerate(s):
    words = k[0].split(" ")[2:]
    words_list = ', '.join([f'p[{x}]' for x in k[2]])
    meta_script += f"""
{meta_prod(k[0])}
def function_{k0}(p):
    return {k[1].__name__}({words_list})\n
"""

meta_script += """\nparser = pg.build()\n"""

with open("hht_parser.py", "w") as mp:
    mp.write(meta_script)
