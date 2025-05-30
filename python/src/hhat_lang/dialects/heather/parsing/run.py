from __future__ import annotations

from pathlib import Path

from arpeggio import visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from hhat_lang.core.code.ast import AST
from hhat_lang.dialects.heather.grammar import WHITESPACE
from hhat_lang.dialects.heather.parsing.visitor import ParserVisitor


def read_grammar() -> str:
    grammar_path = Path(__file__).parent.parent / "grammar" / "grammar.peg"

    if grammar_path.exists():
        return open(grammar_path, "r").read()

    raise ValueError("No grammar found on the grammar directory.")


def parse_grammar() -> ParserPEG:
    grammar = read_grammar()
    return ParserPEG(
        language_def=grammar,
        root_rule_name="program",
        comment_rule_name="comment",
        reduce_tree=True,
        ws=WHITESPACE,
    )


def parse(raw_code: str) -> AST:
    parser = parse_grammar()
    parse_tree = parser.parse(raw_code)
    return visit_parse_tree(parse_tree, ParserVisitor())


def parse_file(file: str | Path) -> AST:
    with open(file, "r") as f:
        data = f.read()

    return parse(data)
