from __future__ import annotations

from pygments.lexer import RegexLexer, bygroups, include, words
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

__all__ = ["HhatLexer"]

WS = r"[\n\t ,;]"
ID = r"[a-zA-Z][a-zA-Z0-9\-_]*"
STRING = r'"[^"]*"'
INT = r"-?\d+"
FLOAT = r"-?\d+\.\d+"
QS = Operator.Quantum
END = r"(?![a-zA-Z0-9\-_])"


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
            (r"//[^\n]*", Comment),
            (r"/-", Comment, "block-comment"),
        ],
        "block-comment": [
            (r"[^-]+", Comment),
            (r"-/", Comment, "#pop"),
            (r"-", Comment),
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
        "qid": [
            (rf"(@)({ID})", bygroups(QS, Name)),
        ],
        "generics": [
            (rf"(\?)(@)({ID})", bygroups(Keyword.Symbol, QS, Keyword.Symbol)),
            (rf"\?{ID}", Keyword.Symbol),
        ],
        "modifier": [
            include("whitespace"),
            (r">", Punctuation.Marker, "#pop"),
            (r"&|\*|\.\.\.", Keyword.Symbol),
            (r"=", Operator),
            include("literals"),
            include("generics"),
            include("qid"),
            (rf"(%)(@)({ID})", bygroups(Operator, QS, Keyword.Type)),
            (rf"(%)({ID})", bygroups(Operator, Keyword.Type)),
            (rf"({ID})(?={WS}*\()", Name.Attribute),
            (r"[()]", Punctuation),
            (ID, Name.Attribute),
        ],
        "imports": [
            include("whitespace"),
            include("comments"),
            (r"\)", Punctuation, "#pop"),
            (rf"(type|fn|metafn|modifier|super-type|const){END}(?={WS}*:)", Keyword.Namespace),
            (r":", Operator),
            (r"[\[\]{}]", Punctuation),
            (r"\.", Operator),
            (r"<", Punctuation.Marker, "modifier"),
            (rf"(@)({ID})", bygroups(QS, Name.Namespace)),
            (ID, Name.Namespace),
        ],
        "root": [
            include("whitespace"),
            include("comments"),
            (
                rf"(use)({WS}*)(\()",
                bygroups(Keyword.Namespace, Whitespace, Punctuation),
                "imports",
            ),
            (rf"#(?:ct|rt)_(?:init|read|write|drop){END}", Keyword.Pseudo),
            (rf"(\$)(@)({ID})", bygroups(Operator, QS, Name)),
            (rf"(\$)({ID})", bygroups(Operator, Name)),
            (
                rf"(fn|metafn)({WS}+)(@)({ID})",
                bygroups(Keyword.Declaration, Whitespace, QS, Name.Entity),
            ),
            (
                rf"(fn|metafn)({WS}+)({ID})",
                bygroups(Keyword.Declaration, Whitespace, Name.Entity),
            ),
            (
                rf"(type)({WS}+)(@)({ID})",
                bygroups(Keyword.Declaration, Whitespace, QS, Name.Class),
            ),
            (
                rf"(type)({WS}+)({ID})",
                bygroups(Keyword.Declaration, Whitespace, Name.Class),
            ),
            (
                rf"(const)({WS}+)(@)({ID})",
                bygroups(Keyword.Declaration, Whitespace, QS, Name.Constant),
            ),
            (
                rf"(modifier)({WS}+)(&|\*|\.\.\.|{ID})",
                bygroups(Keyword.Declaration, Whitespace, Name.Entity),
            ),
            (
                rf"(super-type)({WS}+)({ID})",
                bygroups(Keyword.Declaration, Whitespace, Name.Class),
            ),
            (
                words(("fn", "metafn", "modifier", "super-type", "type", "const"), suffix=END),
                Keyword.Declaration,
            ),
            # (rf"(main|self){END}", Keyword.Pseudo),
            (r"main", Keyword),
            (r"self", Keyword),
            (r"::", Keyword),
            include("literals"),
            (rf"(@)(?:bool|i4|i8{END})", bygroups(QS, Keyword.Type)),
            (
                words(("bool", "u32", "u64", "i32", "i64", "f64", "str"), suffix=END),
                Keyword.Type,
            ),
            (
                rf"(:)({WS}*)(\[)?(@)({ID}){END}(?!{WS}*\()",
                bygroups(Operator, Whitespace, Punctuation, QS, Keyword.Type),
            ),
            (
                rf"(:)({WS}*)(\[)?(\?)(@)({ID}){END}(?!{WS}*\()",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type, QS, Keyword.Type),
            ),
            (
                rf"(:)({WS}*)(\[)?(\?{ID}){END}(?!{WS}*\()",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type),
            ),
            (
                rf"(:)({WS}*)(\[)?({ID}){END}(?!{WS}*\()",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type),
            ),
            (
                rf"(\*)({WS}*)(\[)?(@)({ID}){END}",
                bygroups(Operator, Whitespace, Punctuation, QS, Keyword.Type),
            ),
            (
                rf"(\*)({WS}*)(\[)?(\?)(@)({ID}){END}",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type, QS, Keyword.Type),
            ),
            (
                rf"(\*)({WS}*)(\[)?(\?{ID}){END}",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type),
            ),
            (
                rf"(\*)({WS}*)(\[)?(\?{ID}){END}",
                bygroups(Operator, Whitespace, Punctuation, Keyword.Type),
            ),
            (rf"(?<![a-zA-Z0-9\-_@?%$])_{END}", Keyword.Type),
            (rf"(@)({ID})(?={WS}*\()", bygroups(QS, Name.Function)),
            (rf"({ID})(?={WS}*\()", Name.Function),
            (rf"(@)({ID})", bygroups(QS, Name)),
            (ID, Name),
            (r"<", Punctuation.Marker, "modifier"),
            (r"[(){}\[\]]", Punctuation),
            (r"[.:=]", Operator),
            (r"\*|& ", Operator),
        ],
    }
