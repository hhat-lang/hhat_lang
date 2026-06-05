from __future__ import annotations

from pygments.style import Style
from pygments.token import (
    Token,
    Comment,
    Keyword,
    Name,
    Operator,
    Punctuation,
    String,
    Literal,
    Number
)


class HhatLightStyle(Style):
    """Heather dialect light theme style syntax highlighting."""

    styles = {
        Token: "",
        Comment: "",
        Name: "",
        Name.Variable: "#3d85c6",
        Name.Function: "#2986cc",
        Name.Builtin: "#f6251e",
        Operator: "bold #6a329f",
        Punctuation: "",
        Punctuation.Marker: "bold #16537e",
        Keyword: "",
        Keyword.Declaration: "",
        Keyword.Symbol: "bold #6a329f",
        String: "",
        Literal: "",
        Literal.Boolean: "",
        Number: "",
        Number.Integer: "",
        Number.Float: "",
    }


class HhatDarkStyle(Style):
    """Heather dialect dark theme style syntax highlighting."""

    styles = {
        Token: "",
        Comment: "",
        Name: "",
        Name.Variable: "#9fc5e8",
        Name.Function: "#f9cb9c",
        Name.Builtin: "#f3ec4d",
        Operator: "bold #eb5d39",
        Punctuation: "",
        Punctuation.Marker: "bold #96d2d4",
        Keyword: "",
        Keyword.Declaration: "",
        Keyword.Symbol: "bold #b4a7d6",
        String: "",
        Literal: "",
        Literal.Boolean: "",
        Number: "",
        Number.Integer: "",
        Number.Float: "",
    }
