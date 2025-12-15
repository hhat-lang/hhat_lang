from __future__ import annotations

# Heather whitespaces
WHITESPACE = "\n\t ,;"
# comments
SINGLE_COMMENT = r"\/\/([^\n]*)\n"
MULTILINE_COMMENT = r"\/\-.*?\-\/"
# etc
STRING = r'"([^"]*)"'
INT = r"-?([1-9]\d*|0)"
FLOAT = r"-?\d+\.\d+"

QINT = r"\@-?([1-9]\d*|0)"
