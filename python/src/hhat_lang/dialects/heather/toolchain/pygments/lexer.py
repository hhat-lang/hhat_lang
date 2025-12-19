from __future__ import annotations

from pygments.lexer import RegexLexer, words
from pygments.token import (
    Comment,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    String,
    Whitespace,
)

from hhat_lang.dialects.heather.grammar import (
    FLOAT,
    ID,
    INT,
    MULTILINE_COMMENT,
    QINT,
    SINGLE_COMMENT,
    STRING,
    WHITESPACE,
)

__all__ = ["HhatLexer"]


class HhatLexer(RegexLexer):
    """
    Pygments lexer for Heather dialect syntax.
    """

    name = "H-hat"
    aliases = ["hhat", "hhat-lang"]
    filenames = ["*.hhat", "*.hat"]

    keywords = (
        "main",
        "fn",
        "type",
        "metafn",
        "use",
        "modifier",
        "metamod",
        "self",
        "::",
        "*",
        "&",
    )
    operators = (
        ":",
        "=",
        ".",
        "..",
        "...",
    )
    punctuation = (
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
    )
    builtin_types = (
        "int",
        "float",
        "imag",
        "u32",
        "i32",
        "u64",
        "i64",
        "f32",
        "f64",
        "str",
        "bool",
        "hashmap",
        "sample_t",
        "fn_t",
        "opn_t",
        "bdn_t",
        "opbdn_t",
        "ir_t",
        "@int",
        "@bool",
        "@u2",
        "@u3",
        "@u4",
        "@bell_t",
    )
    bool_literals = ("true", "false", "@true", "@false")

    tokens = {
        "root": [
            (rf"{WHITESPACE}+", Whitespace),
            (SINGLE_COMMENT, Comment.Single),
            (MULTILINE_COMMENT, Comment.Multiline),
            (words(keywords), Keyword.Namespace),
            (words(builtin_types), Name.BuiltinType),
            (words(operators), Operator),
            (words(punctuation), Operator.Punctuation),
            (ID, Name.Identifier),
            (STRING, String),
            (INT, Number.Integer),
            (QINT, Number.QInteger),
            (FLOAT, Number.Float),
            (words(bool_literals, prefix=r"\b", suffix=r"\b"), Literal.Boolean),
        ],
    }
