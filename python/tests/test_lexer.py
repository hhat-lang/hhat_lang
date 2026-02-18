import pytest
from pygments.token import (
    Keyword,
    Name,
    Number,
    String,
    Operator,
    Punctuation,
    Literal,
    Comment,
)
from hhat_lang.dialects.heather.toolchain.pygments.lexer import HhatLexer


@pytest.fixture
def lexer():
    """Initialize the HhatLexer for testing."""
    return HhatLexer()


def get_tokens(lexer, code):
    """Convert code to a list of token type and value tuples, excluding whitespace."""
    return [
        (t, v) for t, v in lexer.get_tokens(code) if str(t) != "Token.Text.Whitespace"
    ]


def test_type_definitions(lexer):
    """Verify that type, struct, and enum definitions are correctly tokenized."""
    code = "type point { x:i32 y:i32 } type status_t { ON OFF }"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Keyword.Declaration, "type")
    assert tokens[1] == (Name.Variable, "point")
    assert tokens[5] == (Name.Builtin, "i32")
    assert tokens[10] == (Keyword.Declaration, "type")
    assert tokens[11] == (Name.Variable, "status_t")


def test_meta_functions(lexer):
    """Verify that meta-fn declarations and calls are identified correctly."""
    code = "meta-fn if(options:[opt-body_t]) ir_t { :: 42 }"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Keyword.Declaration, "meta-fn")
    assert tokens[1] == (Name.Function, "if")
    assert tokens[9] == (Name.Builtin, "ir_t")


def test_modifiers(lexer):
    """Verify that modifiers and the self keyword are identified as Keyword.Declaration."""
    code = "modifier &(self) u32 { ... }"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Keyword.Declaration, "modifier")
    assert tokens[1] == (Keyword.Declaration, "&")
    assert tokens[3] == (Keyword.Declaration, "self")


def test_function_declaration_and_return(lexer):
    """Verify standard function syntax including the return sugar."""
    code = "fn sum(a:i64 b:i64) i64 { :: add(a b) }"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Keyword.Declaration, "fn")
    assert tokens[1] == (Name.Function, "sum")
    assert tokens[12] == (Keyword.Declaration, "::")
    assert tokens[13] == (Name.Function, "add")


def test_complex_import_syntax(lexer):
    """Verify the 'use' keyword and nested import structures."""
    code = "use(type:[math.Point] const:pi)"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Keyword.Declaration, "use")
    assert tokens[2] == (Keyword.Declaration, "type")
    assert tokens[9] == (Keyword.Declaration, "const")


def test_cast_operator(lexer):
    """Verify the cast operator is identified as Keyword.Declaration."""
    code = "v1 * u64"
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Name.Variable, "v1")
    assert tokens[1] == (Keyword.Declaration, "*")
    assert tokens[2] == (Name.Builtin, "u64")


def test_variadic_operator(lexer):
    """Verify that the variadic triple-dot is identified as an operator."""
    code = "..."
    tokens = get_tokens(lexer, code)
    assert tokens[0] == (Operator, "...")
