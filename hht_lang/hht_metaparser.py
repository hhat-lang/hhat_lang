# from hht_lang.hht_new_semantics import s

semantics_prod = "hht_deep_semantics.txt"
semantics_list = "hht_semantics_class_list.txt"
semantics_py = "hht_new_semantics.py"
parser_py = "hht_parser.py"


def create_semantics(semantics_prod_path, semantics_list_path):
    with open(semantics_prod_path, "r") as f1:
        file1 = f1.read().splitlines()
    with open(semantics_list_path, "r") as f2:
        file2 = f2.read().splitlines()

    super_duper = "from hht_core_ast import *\n\ns = [\n    "
    for v0, v1 in zip(file1, file2):
        if v0 and v1:
            super_duper += f"({v0}, {v1}),\n    "
    super_duper += "]\n"
    return super_duper


def save_semantics(data, semantics_py_path):
    with open(semantics_py_path, "w") as f3:
        f3.write(data)


def save_parser(parser_py_path, data):
    with open(parser_py_path, "w") as mp:
        mp.write(data)


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
    meta_script = f"""from hht_lang.hht_core_ast import *
from rply import ParserGenerator
from hht_lang.hht_tokens import tokens
\n
pg = ParserGenerator(list(tokens.keys()))\n
"""

    for k0, k in enumerate(data):
        words = k[0].split(" ")[2:]
        words_list = ', '.join([f'p[{x}]' if x is not None else 'None' for x in k[2]])
        meta_script += f"""
{meta_prod(k[0])}
def function_{k0}(p):
    return {k[1].__name__}({words_list})\n
"""

    meta_script += """\nparser = pg.build()\n"""
    return meta_script


if __name__ == '__main__':
    data1 = create_semantics(semantics_prod, semantics_list)
    s = []
    exec(data1)
    save_semantics(data1, semantics_py)
    meta_script = create_parser_file(s)
    save_parser(parser_py, meta_script)
