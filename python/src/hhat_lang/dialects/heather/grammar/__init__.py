from __future__ import annotations

WHITESPACE = "\n\t ,;"

SINGLE_COMMENT = r"\/\/([^\n]*)\n"
MULTILINE_COMMENT = r"\/\-.*?\-\/"

STRING = r'"([^"]*)"'
INT = r"-?([1-9]\d*|0)"
FLOAT = r"-?\d+\.\d+"
QINT = r"\@-?([1-9]\d*|0)"

ID = r"@?[a-zA-Z][a-zA-Z0-9\-_]*"
