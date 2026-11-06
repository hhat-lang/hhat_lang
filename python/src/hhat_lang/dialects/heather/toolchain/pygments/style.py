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
    Number,
)


QUANTUM_LIGHT = "bold #b45309"
QUANTUM_DARK = "bold #f0b23a"

class HhatLightStyle(Style):
    """Heather dialect light theme style syntax highlighting."""

    styles = {
        Token: "",
        Comment: "italic #6b665c",
        Name: "#1f2328",
        Name.Variable: "#1f2328",
        Name.Function: "#1d4ed8",
        Name.Builtin: "#0f766e",
        Operator: "#e69138",
        Punctuation: "#57534e",
        Punctuation.Marker: "#c5c1bb",
        Keyword: "bold #5b21b6",
        Keyword.Declaration: "bold #5b21b6",
        Keyword.Symbol: "bold #9418c0",
        String: "#166534",
        Literal: "#9d174d",
        Literal.Boolean: "#9d174d",
        Number: "#9d174d",
        Number.Integer: "#9d174d",
        Number.Float: "#9d174d",
        Name.Variable.Quantum: QUANTUM_LIGHT,
        Name.Function.Quantum: QUANTUM_LIGHT,
        Name.Builtin.Quantum: QUANTUM_LIGHT,
        Literal.Boolean.Quantum: QUANTUM_LIGHT,
        Number.Integer.Quantum: QUANTUM_LIGHT,
    }


class HhatDarkStyle(Style):
    """Heather dialect dark theme style syntax highlighting."""

    styles = {
        Token: "",
        Comment: "italic #6b665c",
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
        Name.Variable.Quantum: QUANTUM_DARK,
        Name.Function.Quantum: QUANTUM_DARK,
        Name.Builtin.Quantum: QUANTUM_DARK,
        Literal.Boolean.Quantum: QUANTUM_DARK,
        Number.Integer.Quantum: QUANTUM_DARK,
    }