import click
import os
from copy import deepcopy
try:
    from hhat_lang.lexer import lexer
    from hhat_lang.parser import parser
    from hhat_lang.metaparser import create_parser
except ImportError:
    from ..lexer import lexer
    from ..parser import parser
    from ..metaparser import create_parser


TEST_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.hht")
TEST2_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test2.hht")


def code_print(code):
    title_start = "# CODE START #"
    title_end = "# CODE END #"
    header = f"{'#' * len(title_start)}\n{title_start}\n{'#' * len(title_start)}\n"
    footer = f"{'#' * len(title_end)}\n{title_end}\n{'#' * len(title_end)}\n\n"
    print(f"* Code=\n{header}\n{code}\n{footer}")


def test_hht(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    code_print(data)
    return data


def run_lex(data):
    lex = lexer.lex(data)
    lex_print = deepcopy(lex)
    print(f'* Lex= {list(lex_print)}\n')
    return lex


def run_parser(data):
    return parser.parse(data)


def quick_run(file_=""):
    if not file_:
        file_ = "test.hht"
    _d = test_hht(file_)
    _ld = run_lex(_d)
    print(run_parser(_ld))


def test_run(file=TEST2_FILE_PATH):
    title = "Test Run"
    print(f'{"=" * len(title)}\n{title}\n{"=" * len(title)}\n')
    print('\n* running metaparser')
    create_parser()
    code = test_hht(file)
    lex_code = run_lex(code)
    print(f'\n* Parser= {run_parser(lex_code)}\n')


@click.command()
@click.option("--file", default=TEST2_FILE_PATH, help="H-hat code file")
def args_and_run(file):
    test_run(file)


if __name__ == '__main__':
    args_and_run()
