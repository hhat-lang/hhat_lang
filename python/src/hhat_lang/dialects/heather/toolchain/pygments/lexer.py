from __future__ import annotations

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
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

__all__ = ["HeatherLexer", "HhatLexer"]


class HeatherLexer(RegexLexer):
    """
    Pygments lexer for H-hat's Heather dialect syntax.
    
    Provides syntax highlighting for Heather, the reference dialect
    of the H-hat quantum programming language.
    
    .. versionadded:: 0.3.0
    """

    name = "Heather"
    url = "https://docs.hhat-lang.org"
    aliases = ["heather", "hhat", "hhat-heather", "h-hat"]
    filenames = ["*.hat", "*.hhat"]
    mimetypes = ["text/x-heather", "text/x-hhat"]
    version_added = "0.3.0"

    # Keywords
    keywords = (
        "main",
        "fn",
        "type",
        "const",
        "let",
        "use",
        "meta-fn",
        "metafn",
        "modifier",
        "metamod",
        "self",
        "cast",
        "if",
        "match",
        "while",
        "for",
        "return",
        "pipe",
    )

    # Operators
    operators = (
        "::",  # Return operator
        "=>",  # Arrow
        "->",  # Arrow
        ":",   # Type annotation
        "=",   # Assignment
        "*",   # Cast operator / multiply
        "&",   # Reference
        "^",   # Pointer
        "+",
        "-",
        "/",
        "%",
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
        "&&",
        "||",
        "!",
    )

    # Classical primitive types
    classical_types = (
        "i8", "i16", "i32", "i64", "i128",
        "u8", "u16", "u32", "u64", "u128",
        "f32", "f64",
        "bool",
        "str",
        "char",
        "int",
        "float",
    )

    # Quantum primitive types (prefixed with @)
    quantum_types = (
        "@qubit", "@qbit",
        "@int", "@qint",
        "@float", "@qfloat",
        "@bool", "@qbool",
        "@u2", "@u3", "@u4", "@u8", "@u16", "@u32",
        "@bell_t",
    )

    # Built-in complex types
    builtin_types = (
        "hashmap",
        "sample_t",
        "fn_t",
        "optn_t",
        "bdn_t",
        "optbdn_t",
        "opn_t",
        "ir_t",
        "expr_t",
        "opt_body_t",
        "option_t",
        "result_t",
        "tuple",
        "array",
    )

    # Boolean literals
    bool_literals = (
        "true",
        "false",
        "@true",
        "@false",
    )

    # Quantum state literals
    quantum_literals = (
        r"\|0>",
        r"\|1>",
        r"\|00>",
        r"\|01>",
        r"\|10>",
        r"\|11>",
        r"\|\+>",
        r"\|->",
    )

    # Common quantum gates and operations
    quantum_gates = (
        "h", "x", "y", "z",        # Pauli gates
        "s", "t", "sdg", "tdg",    # Phase gates
        "rx", "ry", "rz",          # Rotation gates
        "cnot", "cx", "cy", "cz",  # Controlled gates
        "swap", "ccx", "toffoli",  # Multi-qubit gates
        "measure", "barrier",       # Operations
    )

    # Common built-in functions
    builtins = (
        "print", "println",
        "add", "sub", "mul", "div", "mod",
        "eq", "ne", "lt", "le", "gt", "ge",
        "and", "or", "not",
        "len", "range",
        "read", "write",
        "sync",
    )

    tokens = {
        "root": [
            # Whitespace
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            
            # Comments
            (SINGLE_COMMENT, Comment.Single),
            (MULTILINE_COMMENT, Comment.Multiline),
            
            # Keywords
            (words(keywords, prefix=r"\b", suffix=r"\b"), Keyword),
            
            # Quantum gates (highlight as special functions)
            (words(quantum_gates, prefix=r"\b", suffix=r"\b"), Name.Builtin.Pseudo),
            
            # Built-in functions
            (words(builtins, prefix=r"\b", suffix=r"\b"), Name.Builtin),
            
            # Types
            (words(classical_types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(quantum_types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(builtin_types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            
            # Boolean literals
            (words(bool_literals, prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            
            # Quantum state literals (|0>, |1>, etc.)
            (r"\|[01\+\-]+>", String.Symbol),
            
            # Function definition
            (r"\b(fn|meta-fn|metafn)\s+", Keyword, "funcname"),
            
            # Type definition
            (r"\b(type)\s+", Keyword, "typename"),
            
            # Constant definition
            (r"\b(const)\s+", Keyword, "constname"),
            
            # Modifier definition
            (r"\b(modifier)\s+", Keyword, "modname"),
            
            # Import statements
            (r"\b(use)\s*\(", Keyword, "import"),
            
            # Return operator
            (r"::", Operator.Word),
            
            # Cast operator
            (r"\*", Operator.Word),
            
            # Reference and pointer operators
            (r"[&\^]", Operator.Word),
            
            # Operators
            (r"(=>|->|<=|>=|==|!=|&&|\|\|)", Operator),
            (r"[+\-*/%<>=!]", Operator),
            
            # Punctuation
            (r"[{}()\[\],.;]", Punctuation),
            (r":", Punctuation),
            
            # Numbers
            (QINT, Number.Integer),  # Quantum integers (@42)
            (FLOAT, Number.Float),
            (INT, Number.Integer),
            
            # Strings
            (STRING, String.Double),
            
            # Modifiers in angle brackets
            (r"<(mut|ref|&|\^)>", Keyword.Pseudo),
            
            # Trait identifiers (#Printable, #[Trait1 Trait2])
            (r"#\[", Punctuation, "trait_list"),
            (r"#@?[A-Z][a-zA-Z0-9_\-]*", Name.Decorator),
            
            # Identifiers (including @ prefix for quantum variables)
            (r"@[a-zA-Z][a-zA-Z0-9_\-]*", Name.Variable.Magic),  # Quantum variables
            (r"[a-zA-Z][a-zA-Z0-9_\-]*", Name),
            
            # Path separators in imports
            (r"\.", Punctuation),
        ],
        
        "funcname": [
            (r"[a-zA-Z][a-zA-Z0-9_\-]*", Name.Function, "#pop"),
            (r"\s+", Whitespace),
        ],
        
        "typename": [
            (r"[a-zA-Z][a-zA-Z0-9_\-]*", Name.Class, "#pop"),
            (r"\s+", Whitespace),
        ],
        
        "constname": [
            (r"[a-zA-Z][a-zA-Z0-9_\-]*", Name.Constant, "#pop"),
            (r"\s+", Whitespace),
        ],
        
        "modname": [
            (r"[a-zA-Z&\^*][a-zA-Z0-9_\-]*", Name.Decorator, "#pop"),
            (r"\s+", Whitespace),
        ],
        
        "import": [
            (r"\)", Punctuation, "#pop"),
            (r"(fn|type|const|metafn|metamod)\s*:", Keyword),
            (r"[a-zA-Z][a-zA-Z0-9_\-\.]*", Name.Namespace),
            (r"[\[\],]", Punctuation),
            (r"\s+", Whitespace),
        ],
        
        "trait_list": [
            (r"\]", Punctuation, "#pop"),
            (r"@?[A-Z][a-zA-Z0-9_\-]*", Name.Decorator),
            (r"\s+", Whitespace),
        ],
    }


# Alias for backward compatibility
HhatLexer = HeatherLexer
