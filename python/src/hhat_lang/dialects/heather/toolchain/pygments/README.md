# H-hat Heather Pygments Lexer

This directory contains the Pygments lexer for the H-hat Heather dialect, enabling syntax highlighting in documentation, IDEs, and other tools that use Pygments.

## Files

- **lexer.py**: Main lexer implementation (`HeatherLexer` class)
- **mkdocs_plugin.py**: MkDocs integration for custom formatters
- **__init__.py**: Package exports

## Installation

The lexer is automatically registered when the `hhat-lang` package is installed:

```bash
pip install -e .
```

This registers the lexer via setuptools entry points defined in `pyproject.toml`:

```toml
[project.entry-points."pygments.lexers"]
heather = "hhat_lang.dialects.heather.toolchain.pygments:HeatherLexer"
hhat = "hhat_lang.dialects.heather.toolchain.pygments:HeatherLexer"
```

## Usage

### In MkDocs

Once installed, use the language identifier in code blocks:

````markdown
```heather
main {
    let q:qubit = |0>
    let q2:qubit = h(q)
    print(q2)
}
```
````

Supported aliases: `heather`, `hhat`, `hhat-heather`, `h-hat`

### Command Line

```bash
# Highlight a file to terminal
pygmentize -l heather example.hat

# Generate HTML
pygmentize -l heather -f html -o output.html example.hat

# Use a specific style
pygmentize -l heather -f html -O style=monokai example.hat
```

### Python API

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer

code = '''
main {
    let x:i32 = 42
    print(x)
}
'''

lexer = HeatherLexer()
formatter = HtmlFormatter(style='monokai')
html = highlight(code, lexer, formatter)
print(html)
```

## Lexer Implementation

The `HeatherLexer` class extends `RegexLexer` from Pygments and uses state-based tokenization to handle complex syntax patterns.

### States

1. **root**: Main state for top-level constructs
2. **funcname**: Function name after `fn` keyword
3. **typename**: Type name after `type` keyword
4. **constname**: Constant name after `const` keyword
5. **modname**: Modifier name after `modifier` keyword
6. **import**: Import path after `use` keyword
7. **trait_list**: Trait names in `#[...]` brackets

### Token Types

The lexer uses standard Pygments token types:

- `Keyword`: Language keywords (`fn`, `let`, `if`, etc.)
- `Name.Builtin`: Built-in types (`i32`, `f64`, `qubit`, etc.)
- `Name.Function`: Function names
- `Name.Class`: Type names
- `Name.Constant`: Constant names
- `Name.Variable.Magic`: Quantum variables (`@variable`)
- `String.Symbol`: Quantum states (`|0>`, `|+>`)
- `Operator`: Operators (`::`, `=>`, `*`, etc.)
- `Comment`: Single and multi-line comments
- `Number`: Integer and floating-point literals

### Adding New Syntax

To add support for new syntax:

1. Add the pattern to the appropriate state in `HeatherLexer.tokens`
2. Use standard Pygments token types for consistency
3. Test with various code samples
4. Update documentation

Example:

```python
(r'\b(new_keyword)\b', Keyword),
```

## Grammar Integration

The lexer imports constants from the grammar files:

```python
from hhat_lang.dialects.heather.grammar import (
    CLASSICAL_TYPES,
    QUANTUM_TYPES,
    BUILTIN_TYPES,
    KEYWORDS,
    QUANTUM_GATES,
    QUANTUM_LITERAL_PATTERN
)
```

This ensures the lexer stays synchronized with the language grammar.

## Testing

Test the lexer with example code:

```python
import sys
from pygments import highlight
from pygments.formatters import TerminalFormatter
from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer

code = open('example.hat').read()
lexer = HeatherLexer()
formatter = TerminalFormatter()
sys.stdout.write(highlight(code, lexer, formatter))
```

## Customization

### Custom Token Types

For specialized highlighting (e.g., quantum-specific syntax), you can define custom token types:

```python
from pygments.token import Token

# Custom quantum tokens
QuantumVariable = Token.Name.Variable.Magic
QuantumState = Token.String.Symbol
QuantumGate = Token.Name.Builtin.Pseudo
```

### Custom Styles

Create a custom Pygments style for H-hat:

```python
from pygments.style import Style
from pygments.token import *

class HhatStyle(Style):
    default_style = ""
    styles = {
        Keyword: 'bold #7c4dff',
        Name.Builtin: '#00897b',
        Name.Variable.Magic: '#ab47bc',
        String.Symbol: '#7c4dff',
        Comment: 'italic #9e9e9e',
        # ... more token types
    }
```

Register it in `pyproject.toml`:

```toml
[project.entry-points."pygments.styles"]
hhat = "hhat_lang.dialects.heather.toolchain.pygments:HhatStyle"
```

## Troubleshooting

### Lexer not found

1. Reinstall package: `pip install -e .`
2. Clear Pygments cache: `rm -rf ~/.cache/pygments`
3. Verify registration: `python -c "from pygments.lexers import get_lexer_by_name; print(get_lexer_by_name('heather'))"`

### Incorrect highlighting

1. Check token patterns in `lexer.py`
2. Ensure grammar constants are imported correctly
3. Test with minimal example to isolate issue
4. Check token precedence (earlier patterns match first)

### MkDocs not using lexer

1. Ensure package is installed in same environment as MkDocs
2. Check `pymdownx.highlight` is enabled in `mkdocs.yml`
3. Use correct language identifier in code blocks
4. Rebuild site with `mkdocs build --clean`

## Contributing

When improving the lexer:

1. Keep patterns synchronized with grammar files
2. Use standard Pygments token types when possible
3. Add tests for new syntax patterns
4. Update documentation
5. Test with real code examples
6. Consider performance for large files

## References

- [Pygments Documentation](https://pygments.org/docs/)
- [Pygments Lexer Development](https://pygments.org/docs/lexerdevelopment/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [Pymdownx Extensions](https://facelessuser.github.io/pymdown-extensions/)
