from __future__ import annotations

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Token,
    Whitespace,
)


class HhatDarkStyle(Style):
    """Heather dialect syntax highlighting for the dark (slate) theme."""

    name = "hhat_heather_dark"

    background_color = "#16120d"
    highlight_color = "#2e2618"
    line_number_color = "#6e6553"

    styles = {
        Token: "#e8e2d0",
        Whitespace: "",
        Comment: "italic #8a8170",
        # keywords
        Keyword: "bold #ff8f40",
        Keyword.Declaration: "bold #ff8f40",
        Keyword.Namespace: "nobold #ff8f40",
        Keyword.Pseudo: "bold #f29668",
        # types: same color on every usage; bold when defined
        Keyword.Type: "nobold #ffd173",
        Name.Class: "bold #ffd173",
        # functions: same color on every call; bold when defined
        Name.Function: "#73d0ff",
        Name.Entity: "bold #73d0ff",
        # cast `*` is a call
        Operator.Word: "bold #73d0ff",
        # marks `.` `:` `=` share one color
        Operator: "#f29668",
        # quantum sigil `@` — the only quantum-distinct piece
        Operator.Quantum: "bold #d2a6ff",
        # names
        Name: "#e8e2d0",
        Name.Namespace: "#e8e2d0",
        Name.Variable: "#e8e2d0",
        Name.Constant: "#f28779",
        Name.Attribute: "#f29668",
        Punctuation.Marker: "#73d0ff",
        # literals: strings apart, everything else shares one color
        String: "#aad94c",
        Number: "#95e6cb",
        Literal.Boolean.Quantum: "nobold #95e6cb",
        Punctuation: "#b8b0a0",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Error: "#ff6666",
    }


class HhatLightStyle(Style):
    """Heather dialect syntax highlighting for the light (default) theme."""

    name = "hhat_heather_light"

    background_color = "#faf5ea"
    highlight_color = "#f0e6cf"
    line_number_color = "#a89e8c"

    styles = {
        Token: "#32302b",
        Whitespace: "",
        Comment: "italic #9a9078",
        # keywords: vivid red-orange, clearly apart from types and marks
        Keyword: "bold #c22b00",
        Keyword.Declaration: "bold #c22b00",
        Keyword.Namespace: "nobold #c22b00",
        Keyword.Pseudo: "bold #c22b00",
        # types: deep teal, same color on every usage; bold when defined
        Keyword.Type: "nobold #00756d",
        Name.Class: "bold #00756d",
        # functions: strong blue, same color on every call; bold when defined
        Name.Function: "#0b5fd0",
        Name.Entity: "bold #0b5fd0",
        # cast `*` is a call
        Operator.Word: "bold #0b5fd0",
        # marks `.` `:` `=` share one muted color that recedes
        Operator: "#6f6555",
        # quantum sigil `@` — the only quantum-distinct piece
        Operator.Quantum: "bold #7c22cf",
        # names
        Name: "#32302b",
        Name.Namespace: "#32302b",
        Name.Variable: "#32302b",
        Name.Constant: "#ad186f",
        Name.Attribute: "#9a6700",
        Punctuation.Marker: "#0b5fd0",
        # literals: strings apart, everything else shares one color
        String: "#3e7d1a",
        Number: "#ad186f",
        Literal.Boolean.Quantum: "nobold #ad186f",
        Punctuation: "#7a7261",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Error: "#cc0000",
    }
