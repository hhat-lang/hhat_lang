from __future__ import annotations

from pygments.lexer import RegexLexer, bygroups, words
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


QID = ID.replace('@?', '@', 1)


class HhatLexer(RegexLexer):
    """
    Pygments lexer for Heather dialect syntax.
    """

    name = "H-hat"
    aliases = ["hhat", "hhat-lang", "hhat-heather", "heather"]
    filenames = ["*.hhat", "*.hat"]

    keywords = (
        "main",
        "fn",
        "type",
        "meta-fn",
        "use",
        "modifier",
        "metamod",
        "super-type",
        "const",
        "self",
    )
    symbolic_keywords = ("::", "*", "&", "<", ">")
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
            (rf"[{WHITESPACE}]+", Whitespace),
            (SINGLE_COMMENT, Comment.Single),
            (MULTILINE_COMMENT, Comment.Multiline),
            (words(keywords, suffix=r"\b"), Keyword.Declaration),
            (words(symbolic_keywords), Keyword.Symbol),
            (
                words(tuple(t for t in builtin_types if t.startswith("@")), suffix=r"\b"),
                Name.Builtin.Quantum,
            ),
            (
                words(tuple(t for t in builtin_types if not t.startswith("@")), suffix=r"\b"),
                Name.Builtin,
            ),
            (
                rf"({QID})(\s*)(\()",
                bygroups(Name.Function.Quantum, Whitespace, Punctuation.Marker),
            ),
            (rf"({ID})(\s*)(\()", bygroups(Name.Function, Whitespace, Punctuation.Marker)),
            (words(operators), Operator),
            (words(punctuation), Punctuation.Marker),
            (FLOAT, Number.Float),
            (QINT, Number.Integer.Quantum),
            (INT, Number.Integer),
            (STRING, String),
            (
                words(tuple(b for b in bool_literals if b.startswith("@")), suffix=r"\b"),
                Literal.Boolean.Quantum,
            ),
            (
                words(tuple(b for b in bool_literals if not b.startswith("@")), suffix=r"\b"),
                Literal.Boolean,
            ),
            (QID, Name.Variable.Quantum),
            (ID, Name.Variable),
        ],
    }
