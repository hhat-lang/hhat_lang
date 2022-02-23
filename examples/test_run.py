import click
from hhat_lang.lexer import lexer
from hhat_lang.parser import parser


def test_hht(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    return data


def run_lex(data):
    lex = lexer.lex(data)
    print(f'* Lex= {lex}\n')
    return lex


def run_parser(data):
    return parser.parse(data)


def quick_run(file_=""):
    if not file_:
        file_ = "test.hht"
    _d = test_hht(file_)
    _ld = run_lex(_d)
    print(run_parser(_ld))


@click.command()
@click.option("--file", default="test.hht", help="H-hat code file")
def test_run(file):
    print('Test Run')
    code = test_hht(file)
    lex_code = run_lex(code)
    print(f'\n* Parse= {run_parser(lex_code)}\n')


if __name__ == '__main__':
    test_run()
