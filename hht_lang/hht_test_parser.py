from hht_lang.hht_lexer import lexer
from hht_lang.hht_parser import parser


def test_hht(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    return data


def run_lex(data):
    return lexer.lex(data)


def run_parser(data):
    return parser.parse(data)


def just_run(file_=""):
    if not file_:
        file_ = "test.hht"
    _d = test_hht(file_)
    _ld = run_lex(_d)
    print(run_parser(_ld))


if __name__ == '__main__':
    d = test_hht("../test.hht")
    ld = run_lex(d)
    print(list(ld))
    print(run_parser(ld))
