from __future__ import annotations

from pygments.lexer import RegexLexer, bygroups, words, include
from pygments.token import (
    Comment,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Whitespace,
)

from hhat_lang.dialects.heather.grammar import (
    MULTILINE_COMMENT,
    SINGLE_COMMENT,
)

__all__ = ["HhatLexer"]

WS = "\n\t ,;"
ID = r"[a-zA-Z][a-zA-Z0-9\-_]*"
STRING = r'"[^"]*"'
INT = r"-?\d*"
FLOAT = r"-?\d+\.\d+"
QS = Operator.Quantum
END = r"(?![a-zA-Z0-9\-_])"

QID = ID.replace('@?', '@', 1)


class HhatLexer(RegexLexer):
    """
    Pygments lexer for Heather dialect syntax.
    """

    name = "H-hat"
    aliases = ["hhat", "hhat-lang", "hhat-heather", "heather"]
    filenames = ["*.hhat", "*.hat"]

    tokens = {
        "whitespace": [(rf"{WS}+", Whitespace)],
        "comments": [
            (r"//[^\n]*", Comment.Singleline),
            (r"/-", Comment.Multiline, "block-comment"),
        ],
        "block-comment": [
            (r"[^-]*", Comment.Multiline),
            (r"-/", Comment.Multiline, "#pop"),
            (r"-", Comment.Multiline),
        ],
        "literals": [
            (r'"[^"]*"', String.Double),
            (rf"(@)({FLOAT})", bygroups(QS, Number.Float)),
            (rf"{FLOAT}", Number.Float),
            (rf"(@)({INT})", bygroups(QS, Number.Integer)),
            (rf"{INT}", Number.Integer),
            (words(("@true", "@false")), Literal.Boolean.Quantum),
            (words(("true", "false")), Literal.Boolean),
        ],
        "qid":[(rf"(@)({ID})", bygroups(QS, Name)),],
        "generics": [
            (rf"(\?)(@)({ID})", bygroups(Keyword.Symbol, QS, Keyword.Symbol)),
            (rf"\?{ID}", Keyword.Symbol),
        ],
        "modifier": [
            include("whitespace"),
            (r">", Keyword, "#pop"),
            (r"&|\*|\.\.\.", Keyword.Symbol),
            (r"=", Operator),
            include("literals"),
            include("generics"),
            include("qid"),
            (rf"(%)(@)({ID})", bygroups(Operator, QS, Keyword.Symbol)),
            (rf"(%)({ID})", bygroups(Operator, Keyword.Symbol)),
            (r"",),
        ]

    }

