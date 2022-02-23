import click


def create_semantics(semantics_prod_path, semantics_list_path):
    with open(semantics_prod_path, "r") as f1:
        file1 = f1.read().splitlines()
    with open(semantics_list_path, "r") as f2:
        file2 = f2.read().splitlines()

    meta_semantics = """from core_ast import *

s = [\n    """
    for v0, v1 in zip(file1, file2):
        if v0 and v1:
            meta_semantics += f"({v0}, {v1}),\n    "
    meta_semantics += "]\n"
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
    _meta_script = f"""from core_ast import *
from rply import ParserGenerator
from tokens import tokens
\n
pg = ParserGenerator(list(tokens.keys()))\n
"""

    for k0, k in enumerate(data):
        words_list = ', '.join([f'p[{x}]' if x is not None else 'None' for x in k[2]])
        _meta_script += f"""
{meta_prod(k[0])}
def function_{k0}(p):
    return {k[1].__name__}({words_list})\n
"""

    _meta_script += """\nparser = pg.build()\n#fim!"""
    return _meta_script


@click.command()
@click.option("--sem_prod",
              default="prod_semantics.txt",
              help="semantics production file name")
@click.option("--class_list",
              default="semantics_class_list.txt",
              help="classes and args list input file name for semantics production")
@click.option("--sem_py",
              default="semantics.py",
              help="the new semantics py file name according to prod and class list data")
@click.option("--parser_py",
              default="parser.py",
              help="parser py file name")
def create_parser(sem_prod, class_list, sem_py, parser_py):
    semantics_data = create_semantics(sem_prod, class_list)
    s = []
    exec(semantics_data)
    save_semantics(semantics_data, sem_py)
    meta_script = create_parser_file(s)
    save_parser(parser_py, meta_script)
    print(f'{"-"*10}\nMetaparser\n{"-"*10}\n* Parser generated on file: {parser_py}\n')


if __name__ == '__main__':
    create_parser()
