try:
    from hhat_lang.core_ast import *
except ImportError:
    from core_ast import *
import click
import os

prod_semantics = "prod_semantics.txt"
semantics_list = "semantics_class_list.txt"
semantics_py = "semantics.py"
parser_py = "parser.py"


def split_class_list(str2split):
    splitted_str = str2split.split(" ")
    class_str = splitted_str[0].strip(',')
    list_str = eval(''.join(splitted_str[1:]))
    return class_str, list_str


def create_semantics(semantics_prod_path, semantics_list_path):
    with open(semantics_prod_path, "r") as f1:
        file1 = f1.read().splitlines()
    with open(semantics_list_path, "r") as f2:
        file2 = f2.read().splitlines()
    meta_semantics = []
    for v0, v1 in zip(file1, file2):
        prod_str = v0.strip('"')
        class_str, list_literal = split_class_list(v1)
        meta_semantics.append((prod_str, class_str, list_literal))
    return meta_semantics


def semantics_py_template(data):
    meta_semantics = f"""try:
    from hhat_lang.core_ast import *
except ImportError:
    from core_ast import *
\n\ns = [\n"""
    for k in data:
        meta_semantics += f"    (\"{k[0]}\", {eval(k[1]).__name__}, {k[2]}),\n"
    meta_semantics += f"    ]\n"
    return meta_semantics


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
    _meta_script = f"""try:
    from hhat_lang.core_ast import *
    from hhat_lang.tokens import tokens
except ImportError:
    from core_ast import *
    from tokens import tokens
from rply import ParserGenerator
\n\n
pg = ParserGenerator(list(tokens.keys()))\n
"""

    for k0, k in enumerate(data):
        words_list = ', '.join([f'p[{x}]' if x is not None else 'None' for x in k[2]])
        _meta_script += f"""
{meta_prod(k[0])}
def function_{k0}(p):
    return {eval(k[1]).__name__}({words_list})\n
"""

    _meta_script += """\nparser = pg.build()\n"""
    return _meta_script


def get_path(file_name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        file_name)


def create_parser(sem_prod=prod_semantics,
                  class_list=semantics_list,
                  sem_py=semantics_py,
                  par_py=parser_py):
    sem_prod = get_path(sem_prod)
    class_list = get_path(class_list)
    sem_py = get_path(sem_py)
    par_py = get_path(par_py)

    semantics_data = create_semantics(sem_prod, class_list)
    sem_str_data = semantics_py_template(semantics_data)
    save_semantics(sem_str_data, sem_py)
    meta_script = create_parser_file(semantics_data)
    save_parser(par_py, meta_script)
    title = ' H-hat lang Metaparser '
    header = f'{"=" * len(title)}\n{title}\n{"=" * len(title)}'
    print(f'{header}\n\n* Parser generated on file: {par_py}\n')


@click.command()
@click.option("--sem_prod",
              default=prod_semantics,
              help="semantics production file name")
@click.option("--class_list",
              default=semantics_list,
              help="classes and args list input file name for semantics production")
@click.option("--sem_py",
              default=semantics_py,
              help="the new semantics py file name according to prod and class list data")
@click.option("--parser_py",
              default=parser_py,
              help="parser py file name")
def call_parser(sem_prod, class_list, sem_py, parser_py):
    create_parser(sem_prod, class_list, sem_py, parser_py)


if __name__ == '__main__':
    call_parser()
